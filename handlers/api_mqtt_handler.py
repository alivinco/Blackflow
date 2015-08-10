import libs

__author__ = 'alivinco'
import logging
from libs import msg_template
log = logging.getLogger(__name__)

class ApiMqttHandler:
    sub_topic = "/app/blackflow/commands"
    pub_topic = "/app/blackflow/events"

    def __init__(self,app_manager,mqtt_adapter,context):
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
               self.app_man.reload_app(msg["command"]["default"]["value"])
            if msg_subtype == "load_new_app" :
               self.app_man.load_new_app(msg["command"]["default"]["value"])

            elif msg_subtype == "reload_app_instance":
               self.app_man.reload_app_instance(msg["command"]["default"]["value"])
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
                app_name = msg["command"]["properties"]["name"]
                alias = msg["command"]["properties"]["alias"]
                sub_for = msg["command"]["properties"]["sub_for"]
                pub_to = msg["command"]["properties"]["pub_to"]
                configs = msg["command"]["properties"]["configs"]
                comments = msg["command"]["properties"]["comments"]
                id = self.app_man.configure_app_instance(inst_id,app_name,alias,sub_for,pub_to,configs,comments)
                self.app_man.reload_app_instance(id)
            elif msg_subtype == "delete_app":
                pass
            elif msg_subtype == "delete_app_instance":
                pass
            elif msg_subtype == "get_apps":
                msg = msg_template.generate_msg_template("blackflow","event","blackflow","apps")
                msg["event"]["properties"] = {"apps":self.app_man.get_apps()}
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

        elif msg_type == "config":
            if msg_subtype == "set" :
                pass
            if msg_subtype == "get" :
                pass






