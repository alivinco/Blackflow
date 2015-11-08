import logging
from apps.lib.Pushnotificator_v1.pushover import Client , init
from blackflow.core.app import BfApp

log = logging.getLogger(__name__)

from pushbullet import PushBullet

class Pushnotificator(BfApp):
    name = __name__

    def on_start(self):
        init(self.config_get("pushover_app_token"))

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        msg = self.var_get(triggered_by)["command"]["properties"]
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