import os
import base64
import logging
from blackflow.libs import msg_template
__author__ = 'alivinco'

log = logging.getLogger(__name__)


class ApiMqttHandler:

    def __init__(self,app_manager,mqtt_adapter,context,instance_name):
        self.sub_topic = "/app/blackflow/%s/commands"%instance_name
        self.pub_topic = "/app/blackflow/%s/events"%instance_name
        self.app_man = app_manager
        self.mqtt_adapter = mqtt_adapter
        self.context = context

    def start(self):
        self.mqtt_adapter.subscribe(self.sub_topic)

    def stop(self):
        self.mqtt_adapter.unsubscribe(self.sub_topic)

    def route(self,topic,msg):
        msg_subtype = msg["command"]["subtype"]
        msg_type = msg["command"]["@type"]
        log.info("New blackflow api call type=%s subtype=%s"%(msg_type,msg_subtype))

        if msg_type == "blackflow":
            if msg_subtype == "reload_app" :
               success,error = self.app_man.reload_app(msg["command"]["default"]["value"])
               msg = msg_template.generate_msg_template("blackflow","event","blackflow","reload_app",msg)
               msg["event"]["properties"] = {"error":error}
               msg["event"]["default"]["value"] = success
               self.mqtt_adapter.publish(self.pub_topic,msg)

            if msg_subtype == "load_new_app" :
               self.app_man.load_new_app(msg["command"]["default"]["value"])

            if msg_subtype == "init_new_app":
               success , warn_msg = self.app_man.init_new_app(msg["command"]["default"]["value"],msg["command"]["properties"]["version"])
               event_msg = msg_template.generate_msg_template("blackflow","event","status","code",msg)
               if not success :
                   event_msg["event"]["default"]["value"] = 500
                   event_msg["event"]["properties"] = {"text":warn_msg}
               else :
                   event_msg["event"]["default"]["value"] = 200
               self.mqtt_adapter.publish(self.pub_topic,event_msg)

            elif msg_subtype == "reload_app_instance":
               self.app_man.reload_app_instance(msg["command"]["default"]["value"])
               msg = msg_template.generate_msg_template("blackflow","event","blackflow","reload_app_instance",msg)
               msg["event"]["properties"] = {"error":""}
               msg["event"]["default"]["value"] = True
               self.mqtt_adapter.publish(self.pub_topic,msg)

            elif msg_subtype == "control_app":
                pass
            elif msg_subtype == "add_app":
                app_name = msg["command"]["properties"]["name"]
                sub_for = msg["command"]["properties"]["sub_for"]
                pub_to = msg["command"]["properties"]["pub_to"]
                configs = msg["command"]["properties"]["configs"]
                src = msg["command"]["properties"]["src"]

            elif msg_subtype == "configure_app_instance":
                inst_id = msg["command"]["properties"]["id"]
                app_full_name = msg["command"]["properties"]["app_full_name"]
                alias = msg["command"]["properties"]["alias"]
                sub_for = msg["command"]["properties"]["sub_for"]
                pub_to = msg["command"]["properties"]["pub_to"]
                configs = msg["command"]["properties"]["configs"]
                comments = msg["command"]["properties"]["comments"]
                schedules = msg["command"]["properties"]["schedules"]

                id = self.app_man.configure_app_instance(inst_id,app_full_name,alias,sub_for,pub_to,configs,comments,schedules=schedules)
                # self.app_man.reload_app_instance(id)

            elif msg_subtype == "delete_app":
                app_full_name = msg["command"]["default"]["value"]
                self.app_man.delete_app(app_full_name)

            elif msg_subtype == "delete_app_instance":
                inst_id = int(msg["command"]["default"]["value"])
                self.app_man.delete_app_instance(inst_id)

            elif msg_subtype == "control_app_instance":
                inst_id = int(msg["command"]["default"]["value"])
                action = msg["command"]["properties"]["action"]
                if action == "START":
                    self.app_man.start_app_instance(inst_id)
                elif action == "PAUSE":
                    self.app_man.pause_app_instance(inst_id)
                if action == "STOP":
                    self.app_man.stop_app_instance(inst_id)

            elif msg_subtype == "get_apps":
                msg = msg_template.generate_msg_template("blackflow","event","blackflow","apps")
                msg["event"]["properties"] = {"apps":self.app_man.get_app_manifests()}
                self.mqtt_adapter.publish(self.pub_topic,msg)

            elif msg_subtype == "get_app_instances":
                msg = msg_template.generate_msg_template("blackflow","event","blackflow","app_instances")

                msg["event"]["properties"] = {"app_instances":self.app_man.get_app_configs()}
                self.mqtt_adapter.publish(self.pub_topic,msg)

            elif msg_subtype == "context_get":
                msg = msg_template.generate_msg_template("blackflow","event","blackflow","context")
                msg["event"]["properties"] = self.context.get_dict()
                self.mqtt_adapter.publish(self.pub_topic,msg)

            elif msg_subtype == "analytics_get":
                msg = msg_template.generate_msg_template("blackflow","event","blackflow","analytics")
                msg["event"]["properties"] = {"link_counters":self.context.analytics.get_all_link_counters()}
                self.mqtt_adapter.publish(self.pub_topic,msg)

            elif msg_subtype == "context_set":
                pass
            elif msg_subtype == "download_app":
                app_name = msg["command"]["default"]["value"]
            elif msg_subtype == "upload_app":
                pass

        elif msg_type == "file":
            if msg_subtype == "download":
                # absolute path to app directory
                file_name = msg["command"]["default"]["value"]
                full_path = os.path.join(self.app_man.apps_dir_path,"lib",file_name)
                with open(full_path, "rb") as app_file:
                    bin_data = base64.b64encode(app_file.read())
                msg = msg_template.generate_msg_template("blackflow","event","file","download",msg)
                msg["event"]["default"]["value"] = file_name
                msg["event"]["properties"]["bin_data"] = bin_data
                self.mqtt_adapter.publish(self.pub_topic,msg)

            if msg_subtype == "upload":
                name = msg["command"]["properties"]["name"]
                type = msg["command"]["properties"]["type"]
                data = msg["command"]["properties"]["bin_data"]
                post_save_action = msg["command"]["properties"]["post_save_action"] if "post_save_action" in msg["command"]["properties"] else None
                full_path = os.path.join(self.app_man.apps_dir_path,"lib",name)
                bin_data = base64.b64decode(data)
                with open(full_path, "wb") as app_file:
                    app_file.write(bin_data)
                if post_save_action == "reload_manifest":
                    self.app_man.load_app_manifests()


        elif msg_type == "config":
            if msg_subtype == "set" :
                pass
            if msg_subtype == "get" :
                pass






