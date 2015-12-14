import logging
from blackflow.core.app import BfApp

log = logging.getLogger("LightsControl")


class LightsControl(BfApp):
    name = "LightsControl"

    def on_message(self,triggered_by):
        # self.publish("/dev/zw/75/bin_switch/1/commands","binary.switch",True)
        log.info("LightControll app was triggered by %s"%triggered_by)
        if self.self.var_get(triggered_by)["event"]["default"]["value"]:
            self.context.set("lights_state", "off", self)
            self.publish("switch", self.lights_control())
            log.info("Actionnnn by %s"%self.alias)
        else :
            log.info("Lights are already ON test3")
        
    def lights_control(self,state):
        return {
                     "origin": {
                      "vendor": "Blackflow",
                      "@id": "smartly_ios",
                      "@type": "app"
                     },
                     "uuid": "86f93c70-6c47-4cfc-91eb-30d3b069e417",
                     "creation_time": 1385815582,
                     "command": {
                      "default": {
                       "value": state
                      },
                      "subtype": "switch",
                      "@type": "binary",
                     },
                     "spid": "S-451-12",
                     "@context": "http://smartly.no/context"
                }


