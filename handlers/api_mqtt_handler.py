__author__ = 'alivinco'
import logging

log = logging.getLogger("bf_api_mqtt_handl")

class ApiMqttHandler:
    sub_topic = "mqtt:/app/blackflow/commands"
    pub_topic = "mqtt:/app/blackflow/events"

    def __init__(self,app_manager,mqtt_adapter):
        self.app_man = app_manager
        self.mqtt_adapter = mqtt_adapter

    def start(self):
        self.mqtt_adapter.subscribe(self.sub_topic)

    def stop(self):
        self.mqtt_adapter.unsubscribe(self.sub_topic)

    def route(self,topic,msg):

        msg_subtype = msg["command"]["subtype"]
        msg_type = msg["command"]["@type"]

        if msg_type == "blackflow":
            if msg_subtype == "reload_app" :
               self.app_man.reload_app(msg["command"]["default"]["value"])
            elif msg_subtype == "reload_app_instance":
               self.app_man.reload_app_instance(msg["command"]["default"]["value"])
            elif msg_subtype == "control_app":
                pass
            elif msg_subtype == "upload_app":
                pass
            elif msg_subtype == "configure_app_instance":
                pass
            elif msg_subtype == "delete_app":
                pass
            elif msg_subtype == "delete_app_instance":
                pass
            elif msg_subtype == "get_apps":
                pass
            elif msg_subtype == "get_app_instances":
                pass

        elif msg_type == "config":
            if msg_subtype == "set" :
                pass
            if msg_subtype == "get" :
                pass






