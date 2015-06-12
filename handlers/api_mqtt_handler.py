__author__ = 'alivinco'

class ApiMqttHandler:
    sub_topic = "/app/blackflow/commands"
    pub_topic = "/app/blackflow/events"

    def __init__(self,app_manager):
        self.app_man = app_manager

    def router(self,topic,msg):
        msg_subtype = ""
        msg_type = ""

        if msg_type == "blackflow":
            if msg_subtype == "reload_app" :
               self.app_man.reload_app(msg["command"]["default"]["value"])
            elif msg_subtype == "reload_app_instance":
               self.app_man.reload_app_instance(msg["command"]["default"]["value"],msg["command"]["properties"]["app_name"])
            elif msg_subtype == "start_app":
                pass
            elif msg_subtype == "stop_app":
                pass
            elif msg_subtype == "upload_app":
                pass
            elif msg_subtype == "configure_app":
                pass
            elif msg_subtype == "get_apps":
                pass
            elif msg_subtype == "get_app_instances":
                pass
            elif msg_subtype == "get_app_configs":
                pass

        elif msg_type == "config":
            if msg_subtype == "set" :
                pass
            if msg_subtype == "get" :
                pass






