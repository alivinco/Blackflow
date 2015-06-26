import logging
from core.app import BfApp

log = logging.getLogger(__name__)

from pushbullet import PushBullet

class Pushnotificator(BfApp):
    name = __name__

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        msg = self.var_get(triggered_by)["command"]["properties"]
        self.push_msg_to_device(msg["title"],msg["body"],msg["address"])

    def push_msg_to_device(self,title,body,device=None):
        pushb = PushBullet(self.config_get("api_key"))
        pushb.push_note(title,body)

