import os
import base64
import logging
from blackflow.libs.app_store import AppStore
from libs.iot_msg import IotMsg

__author__ = 'alivinco'

log = logging.getLogger(__name__)


class ApiMqttHandler:
    def __init__(self, app_manager, mqtt_adapter, context, instance_name, configs={}):
        self.discovery_sub_topic = "/discovery/commands"
        self.discovery_pub_topic = "/discovery/events"
        self.sub_topic = "/app/blackflow/%s/commands" % instance_name
        self.pub_topic = "/app/blackflow/%s/events" % instance_name
        self.app_man = app_manager
        self.mqtt_adapter = mqtt_adapter
        self.context = context
        self.configs = configs
        self.instance_name = instance_name
        # self.app_store = AppStore(self.configs["app_store"]["api_url"], self.configs["apps_dir_path"])

    def start(self):
        self.mqtt_adapter.subscribe(self.discovery_sub_topic)
        self.mqtt_adapter.subscribe(self.sub_topic)

    def stop(self):
        self.mqtt_adapter.unsubscribe(self.sub_topic)
        self.mqtt_adapter.subscribe(self.discovery_sub_topic)

    def reply_with_status(self, code, description="", request_msg=None):
        """
        Generates unified confirmation reply-event to received command
        :param code: result code
        :param description: result description
        :param request_msg: request message , is used to extract request uuid and use it as correlation id (corr_id)
        """
        event_msg = IotMsg.new_iot_msg("blackflow", "event", "status", "code")
        event_msg.set_corr_id_from_iotmsg(request_msg)
        event_msg.set_default(code)
        event_msg.set_properties({"text": description})
        self.mqtt_adapter.publish(self.pub_topic, event_msg)

    def route(self, topic, msg):
        msg = IotMsg.new_iot_msg_from_dict("blackflow",msg)

        msg_type = msg.get_msg_class()
        msg_subtype = msg.get_msg_subclass()
        log.info("New blackflow api call type=%s subtype=%s" % (msg_type, msg_subtype))
        if msg_type == "discovery":
            if msg_subtype == "query":
                resp_msg = IotMsg.new_iot_msg("blackflow", "event", "discovery", "response")
                resp_msg.set_corr_id_from_iotmsg(msg)
                app_full_name = "/app/blackflow/%s" % self.instance_name
                resp_msg.set_default(app_full_name)
                resp_msg.set_properties({"type": "app",
                                         "name": app_full_name,
                                         "desc": "Lightweight application container",
                                         "sdk": "py_blackflow_v1",
                                         "ip_addr": "127.0.0.1"
                                         })

                self.mqtt_adapter.publish(self.discovery_pub_topic, resp_msg.get_dict())

        elif msg_type == "blackflow":
            if msg_subtype == "reload_app":
                success, error = self.app_man.reload_app(msg.get_default_value())
                resp_msg = IotMsg.new_iot_msg("blackflow", "event", "blackflow", "reload_app")
                resp_msg.set_corr_id_from_iotmsg(msg)
                resp_msg.set_default(success)
                resp_msg.set_properties({"error": error})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg.get_dict())

            if msg_subtype == "load_app_class":
                self.app_man.load_app_class(msg.get_default_value())

            if msg_subtype == "init_new_app":
                props = msg.get_properties()
                success, warn_msg = self.app_man.init_new_app(props["developer"], msg.get_default_value(),props["version"])
                event_msg = IotMsg.new_iot_msg("blackflow", "event", "status", "code")
                event_msg.set_corr_id_from_iotmsg(msg)
                if not success:
                    event_msg.set_default(500)
                    event_msg.set_properties({"text": warn_msg})
                else:
                    event_msg.set_default(200)
                self.mqtt_adapter.publish(self.pub_topic, event_msg.get_dict())

            elif msg_subtype == "reload_app_instance":
                self.app_man.reload_app_instance(msg.get_default_value())
                resp_msg = IotMsg.new_iot_msg("blackflow", "event","blackflow", "reload_app_instance")
                resp_msg.set_corr_id_from_iotmsg(msg)
                resp_msg.set_properties({"error": ""})
                resp_msg.set_default(True)
                self.mqtt_adapter.publish(self.pub_topic, resp_msg.get_dict())

            elif msg_subtype == "control_app":
                pass
            elif msg_subtype == "add_app":
                props = msg.get_properties()
                app_name = props["name"]
                sub_for = props["sub_for"]
                pub_to = props["pub_to"]
                configs = props["configs"]
                src = props["src"]

            elif msg_subtype == "configure_app_instance":
                props = msg.get_properties()
                inst_id = props["id"]
                app_full_name = props["app_full_name"]
                alias = props["alias"]
                sub_for = props["sub_for"]
                pub_to = props["pub_to"]
                configs = props["configs"]
                comments = props["comments"]
                schedules = props["schedules"]

                id = self.app_man.configure_app_instance(inst_id, app_full_name, alias, sub_for, pub_to, configs, comments, schedules=schedules)
                self.reply_with_status(200, str(id), msg)
                # self.app_man.reload_app_instance(id)

            elif msg_subtype == "delete_app":
                # deafult value - app full name
                self.app_man.delete_app(msg.get_default_value())
                self.reply_with_status(200, "", msg)

            elif msg_subtype == "delete_app_instance":
                # default value - app_instance
                self.app_man.delete_app_instance(msg.get_default_value())
                self.reply_with_status(200, "", msg)

            elif msg_subtype == "control_app_instance":
                inst_id = int(msg.get_default_value())
                action = msg.get_properties()["action"]
                if action == "START":
                    self.app_man.start_app_instance(inst_id)
                elif action == "PAUSE":
                    self.app_man.pause_app_instance(inst_id)
                if action == "STOP":
                    self.app_man.stop_app_instance(inst_id)
                self.reply_with_status(200, "", msg)

            elif msg_subtype == "get_apps":
                resp_msg = IotMsg.new_iot_msg("blackflow", "event", "blackflow", "apps")
                resp_msg.set_corr_id_from_iotmsg(msg)
                resp_msg.set_properties({"apps": self.app_man.get_app_manifests()})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg.get_dict())

            elif msg_subtype == "get_app_instances":
                resp_msg = IotMsg.new_iot_msg("blackflow", "event", "blackflow", "app_instances")
                resp_msg.set_corr_id_from_iotmsg(msg)
                resp_msg.set_properties({"app_instances": self.app_man.get_app_configs()})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg.get_dict())

            elif msg_subtype == "context_get":
                resp_msg = IotMsg.new_iot_msg("blackflow", "event", "blackflow", "context")
                resp_msg.set_corr_id_from_iotmsg(msg)
                resp_msg.set_properties(self.context.get_dict())
                self.mqtt_adapter.publish(self.pub_topic, resp_msg.get_dict())

            elif msg_subtype == "analytics_get":
                resp_msg = IotMsg.new_iot_msg("blackflow", "event", "blackflow", "analytics")
                resp_msg.set_corr_id_from_iotmsg(msg)
                resp_msg.set_properties({"link_counters": self.context.analytics.get_all_link_counters()})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg.get_dict())

            elif msg_subtype == "context_set":
                pass
            elif msg_subtype == "download_app":
                pass
            elif msg_subtype == "upload_app":
                pass
        elif msg_type == "app_store":
            if msg_subtype == "upload_app":
                # default value = app_full_name
                props = msg.get_properties()
                app_store_server = props["app_store_url"]
                app_store_token = props["sec_token"]
                app_store = AppStore(app_store_server, self.configs["apps_dir_path"])
                app_id, err = app_store.pack_and_upload_app(msg.get_default_value())
                if not err:
                    self.reply_with_status(200, "app_id=" + app_id, msg)
                else:
                    log.error("App can't be aploaded because of error %s" % err)
                    self.reply_with_status(500, err, msg)

            elif msg_subtype == "download_app":
                props = msg.get_properties()
                app_store_server = props["app_store_url"]
                app_store_token = props["sec_token"]
                app_store = AppStore(app_store_server, self.configs["apps_dir_path"])
                app_full_name = app_store.download_and_unpack_app(msg.get_default_value())
                self.app_man.load_app_manifest(app_full_name)
                self.reply_with_status(200, "app_full_name=" + app_full_name, msg)

        elif msg_type == "file":
            if msg_subtype == "download":
                # absolute path to app directory
                file_name = msg.get_default_value()
                full_path = os.path.join(self.app_man.apps_dir_path, "lib", file_name)
                with open(full_path, "rb") as app_file:
                    bin_data = base64.b64encode(app_file.read())
                resp_msg = IotMsg.new_iot_msg("blackflow", "event", "file", "download")
                resp_msg.set_corr_id_from_iotmsg(msg)
                resp_msg.set_default(file_name)
                resp_msg.set_properties({"bin_data":bin_data})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg.get_dict())

            if msg_subtype == "upload":
                props = msg.get_properties()
                name = props["name"]
                type = props["type"]
                data = props["bin_data"]
                post_save_action = props["post_save_action"] if "post_save_action" in props else None
                full_path = os.path.join(self.app_man.apps_dir_path, "lib", name)
                bin_data = base64.b64decode(data)
                with open(full_path, "wb") as app_file:
                    app_file.write(bin_data)
                if post_save_action == "reload_manifest":
                    self.app_man.load_app_manifests()


        elif msg_type == "config":
            if msg_subtype == "set":
                pass
            if msg_subtype == "get":
                pass
