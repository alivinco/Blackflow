import os
import base64
import logging
from blackflow.libs.app_store import AppStore
from blackflow.libs.iot_msg_lib.iot_msg import MsgType, IotMsg
from blackflow.libs.utils import get_local_ip

__author__ = 'alivinco'

log = logging.getLogger(__name__)

class ApiMqttHandler:
    def __init__(self, app_manager, mqtt_adapter, context, instance_name, configs={}):
        self.discovery_sub_topic = "jim1/discovery/commands"
        self.discovery_pub_topic = "jim1/discovery/events"
        self.sub_topic = "jim1/app/blackflow/%s/commands" % instance_name
        self.pub_topic = "jim1/app/blackflow/%s/events" % instance_name
        self.app_man = app_manager
        self.mqtt_adapter = mqtt_adapter
        self.context = context
        self.configs = configs
        self.instance_name = instance_name
        self.local_ip = get_local_ip()
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
        event_msg = IotMsg("blackflow", MsgType.EVT, "status", "code", req_msg=request_msg)
        event_msg.set_default(code)
        event_msg.set_properties({"text": description})
        self.mqtt_adapter.publish(self.pub_topic, event_msg)

    def route(self, topic, iot_msg):

        msg_type = iot_msg.get_msg_class()
        msg_subtype = iot_msg.get_msg_subclass()
        log.info("New blackflow api call type=%s subtype=%s" % (msg_type, msg_subtype))
        if msg_type == "discovery":
            if msg_subtype == "find":
                resp_msg = IotMsg("blackflow", MsgType.EVT , "discovery", "report", req_msg=iot_msg)
                app_full_name = "/app/blackflow/%s" % self.instance_name
                resp_msg.set_default(app_full_name)
                resp_msg.set_properties({"type": "app",
                                         "name": "blackflow",
                                         "uri": app_full_name,
                                         "sdk": "py_blackflow_v1",
                                         "ip": self.local_ip,
                                         "props": {"container_id": self.instance_name}
                                         })

                self.mqtt_adapter.publish(self.discovery_pub_topic, resp_msg)

        elif msg_type == "blackflow":
            if msg_subtype == "reload_app":
                success, error = self.app_man.reload_app(iot_msg.get_default_value())
                resp_msg = IotMsg("blackflow", MsgType.EVT, "blackflow", "reload_app", req_msg=iot_msg)
                resp_msg.set_default(success)
                resp_msg.set_properties({"error": error})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg)

            if msg_subtype == "load_app_class":
                self.app_man.load_app_class(iot_msg.get_default_value())

            if msg_subtype == "init_new_app":
                props = iot_msg.get_properties()
                success, warn_msg = self.app_man.init_new_app(props["developer"], iot_msg.get_default_value(), props["version"])
                if not success:
                    self.reply_with_status(500,warn_msg,iot_msg)
                else:
                    self.reply_with_status(200,warn_msg,iot_msg)

            elif msg_subtype == "reload_app_instance":
                self.app_man.reload_app_instance(iot_msg.get_default_value())
                resp_msg = IotMsg("blackflow", MsgType.EVT,"blackflow", "reload_app_instance",req_msg=iot_msg)
                resp_msg.set_properties({"error": ""})
                resp_msg.set_default(True)
                self.mqtt_adapter.publish(self.pub_topic, resp_msg)

            elif msg_subtype == "control_app":
                pass
            elif msg_subtype == "add_app":
                props = iot_msg.get_properties()
                app_name = props["name"]
                sub_for = props["sub_for"]
                pub_to = props["pub_to"]
                configs = props["configs"]
                src = props["src"]

            elif msg_subtype == "configure_app_instance":
                props = iot_msg.get_properties()
                inst_id = props["id"]
                app_full_name = props["app_full_name"]
                alias = props["alias"]
                sub_for = props["sub_for"]
                pub_to = props["pub_to"]
                configs = props["configs"]
                comments = props["comments"]
                schedules = props["schedules"]

                id = self.app_man.configure_app_instance(inst_id, app_full_name, alias, sub_for, pub_to, configs, comments, schedules=schedules)
                self.reply_with_status(200, str(id), iot_msg)
                # self.app_man.reload_app_instance(id)

            elif msg_subtype == "delete_app":
                # deafult value - app full name
                self.app_man.delete_app(iot_msg.get_default_value())
                self.reply_with_status(200, "", iot_msg)

            elif msg_subtype == "delete_app_instance":
                # default value - app_instance
                self.app_man.delete_app_instance(iot_msg.get_default_value())
                self.reply_with_status(200, "", iot_msg)

            elif msg_subtype == "control_app_instance":
                inst_id = int(iot_msg.get_default_value())
                action = iot_msg.get_properties()["action"]
                if action == "START":
                    self.app_man.start_app_instance(inst_id)
                elif action == "PAUSE":
                    self.app_man.pause_app_instance(inst_id)
                if action == "STOP":
                    self.app_man.stop_app_instance(inst_id)
                self.reply_with_status(200, "", iot_msg)

            elif msg_subtype == "get_apps":
                resp_msg = IotMsg("blackflow", MsgType.EVT, "blackflow", "apps", req_msg=iot_msg)
                resp_msg.set_properties({"apps": self.app_man.get_app_manifests()})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg)

            elif msg_subtype == "get_app_instances":
                resp_msg = IotMsg("blackflow", MsgType.EVT, "blackflow", "app_instances", req_msg=iot_msg)
                resp_msg.set_properties({"app_instances": self.app_man.get_app_configs()})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg)

            elif msg_subtype == "context_get":
                resp_msg = IotMsg("blackflow", MsgType.EVT, "blackflow", "context", req_msg=iot_msg)
                result = self.context.get_dict()
                for k , v in result.iteritems():
                    if isinstance(v["value"],IotMsg) :
                        v["value"] = str(v["value"])
                    # result[k]=v

                resp_msg.set_properties(result)
                self.mqtt_adapter.publish(self.pub_topic, resp_msg)

            elif msg_subtype == "analytics_get":
                resp_msg = IotMsg("blackflow", MsgType.EVT, "blackflow", "analytics" ,req_msg=iot_msg)
                resp_msg.set_properties({"link_counters": self.context.analytics.get_all_link_counters()})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg)

            elif msg_subtype == "context_set":
                pass
            elif msg_subtype == "download_app":
                pass
            elif msg_subtype == "upload_app":
                pass
        elif msg_type == "app_store":
            if msg_subtype == "upload_app":
                # default value = app_full_name
                props = iot_msg.get_properties()
                app_store_server = props["app_store_url"]
                id_token = props["id_token"]
                app_store = AppStore(app_store_server, self.configs["apps_dir_path"])
                app_id, err = app_store.pack_and_upload_app(iot_msg.get_default_value(),id_token)
                if not err:
                    self.reply_with_status(200, "app_id=" + app_id, iot_msg)
                else:
                    log.error("App can't be aploaded because of error %s" % err)
                    self.reply_with_status(500, err, iot_msg)

            elif msg_subtype == "download_app":
                props = iot_msg.get_properties()
                app_store_server = props["app_store_url"]
                id_token = props["id_token"]
                app_store = AppStore(app_store_server, self.configs["apps_dir_path"])
                app_full_name = app_store.download_and_unpack_app(iot_msg.get_default_value(),id_token)
                if not self.app_man.get_app_manifest(app_full_name):
                    self.app_man.load_app_manifest(app_full_name)
                self.reply_with_status(200, "app_full_name=" + app_full_name, iot_msg)

        elif msg_type == "file":
            if msg_subtype == "download":
                # absolute path to app directory
                file_name = iot_msg.get_default_value()
                full_path = os.path.join(self.app_man.apps_dir_path, "lib", file_name)
                with open(full_path, "rb") as app_file:
                    bin_data = base64.b64encode(app_file.read())
                resp_msg = IotMsg("blackflow", MsgType.EVT, "file", "download", req_msg=iot_msg)
                resp_msg.set_default(file_name)
                resp_msg.set_properties({"bin_data":bin_data})
                self.mqtt_adapter.publish(self.pub_topic, resp_msg)

            if msg_subtype == "upload":
                props = iot_msg.get_properties()
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
                self.reply_with_status(200, "", iot_msg)


        elif msg_type == "config":
            if msg_subtype == "set":
                pass
            if msg_subtype == "get":
                pass
