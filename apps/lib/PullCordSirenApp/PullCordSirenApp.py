import logging
from libs.msg_template import generate_msg_template
from core.app import BfApp

log = logging.getLogger("PullCordSirenApp")

class PullCordSirenApp(BfApp):
    name = "PullCordSirenApp"

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        if self.var_get("pull_cord_is_on"):
            self.var_set("pull_cord_is_on", False )
            self.publish("siren_control", self.siren_control("chime"))
        else:
            self.var_set("pull_cord_is_on", True )
            self.publish("siren_control", self.siren_control("chime"))
            log.info("Turning siren 5 on  %s"%self.alias)

    def siren_control(self,state):
        msg = generate_msg_template(self.name,"command","mode","siren")
        msg["command"]["default"]["value"] = state
        return msg



