import logging
from core.app import BfApp

log = logging.getLogger("LightsControl")

class LightsControl(BfApp):
    name = "LightsControl"

    def run(self,triggered_by):
        # self.publish("/dev/zw/75/bin_switch/1/commands","binary.switch",True)
        log.info("LightControll app was triggered by %s"%triggered_by)
        if self.context.get(self.sub_for["motion_sensor"])["event"]["default"]["value"]:
            self.context.set("lights_state", "off", self)
            self.context.set(self.pub_to["switch"], self.lights_on(), self)
            log.info("Actionnnn by %s"%self.alias)
        else :
            log.info("Lights are already ON ")

    def lights_on(self):
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
                       "value": True
                      },
                      "subtype": "switch",
                      "@type": "binary",
                     },
                     "spid": "S-451-12",
                     "@context": "http://smartly.no/context"
                }



