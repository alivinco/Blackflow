import logging
from libs.msg_template import generate_msg_template
from core.app import BfApp

log = logging.getLogger("PullCordSirenApp")

class PullCordSirenApp(BfApp):
    name = __name__
    def on_start(self):
        self.is_alarms_situation = False

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        situation = self.var_get(triggered_by)["event"]["default"]["value"]
        if situation == "medical" and not self.is_alarms_situation:
            self.publish("siren_control", self.siren_control("chime"))
            self.publish("push_cmd_local",{"command":{"properties":{"title":"Emergency","body":"Cord has been pushed on","address":""}}})
            self.is_alarms_situation = True

        elif situation == "cancel" or self.is_alarms_situation:
            self.publish("push_cmd_local",{"command":{"properties":{"title":"Emergency cancel","body":"Everything is ok","address":""}}})
            self.is_alarms_situation = False

    def siren_control(self,state):
        msg = generate_msg_template(self.name,"command","mode","siren")
        msg["command"]["default"]["value"] = state
        return msg




