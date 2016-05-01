import logging
from apps.lib.alivinco_nPushnotificator_v1.pushover import Client , init
from blackflow.core.app import BfApp
log = logging.getLogger(__name__)

from pushbullet import PushBullet


class Pushnotificator(BfApp):
    name = __name__

    def on_start(self):
        init(self.config_get("pushover_app_token"))
    '''
    Msg has folowing properties :
     transport - "pushbullet" or "pushover"
     title - message title 
     body - message body
     address - specific device , not in use so far 
    
    '''
    def on_message(self,topic,iot_msg):
        log.info("%s app was triggered by %s"%(self.name,topic))
        msg = iot_msg.get_properties()
        transport = msg["transport"] if "transport" in msg else None
        if transport == "pushbullet":
            self.pushbullet_msg_to_device(msg["title"],msg["body"],msg["address"])
        else :
            self.pushover_msg_to_device(msg["title"],msg["body"],msg["address"])

    def pushbullet_msg_to_device(self,title,body,device=None):
        log.info("Sending notification to Pushbullet service")
        pushb = PushBullet(self.config_get("pushbullet_api_key"))
        pushb.push_note(title,body)

    def pushover_msg_to_device(self,title,body,device=None):
        log.info("Sending notification to Pushover service")
        Client(self.config_get("pushover_client_id")).send_message(body, title=title, timestamp=True)