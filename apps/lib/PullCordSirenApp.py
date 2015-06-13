import logging
from core.app import BfApp

log = logging.getLogger("LightsControl")

class PullCordSirenApp(BfApp):
    name = "PullCordSirenApp"

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        if self.context.get("pull_cord_is_on"):
            self.context.set("pull_cord_is_on", False , self)
            self.context.set(self.pub_to["siren_control"], self.siren_control("chime"), self)
        else:
            self.context.set("pull_cord_is_on", True , self)
            self.context.set(self.pub_to["siren_control"], self.siren_control("chime"), self)
            log.info("Actionnnn by %s"%self.alias)

    def siren_control(self,state):
        return {
                     "origin": {
                      "@id": "blackflow",
                      "@type": "app"
                     },
                     "uuid": "86f93c70-6c47-4cfc-91eb-30d3b069e417",
                     "creation_time": 1385815582,
                     "command": {
                      "default": {
                       "value": state
                      },
                      "subtype": "siren",
                      "@type": "mode"
                     },
                     "spid": "S-451-12",
                     "@context": "http://smartly.no/context"
                }



