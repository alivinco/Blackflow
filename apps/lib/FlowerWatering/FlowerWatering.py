import logging
import time
from libs.msg_template import generate_msg_template
from core.app import BfApp

log = logging.getLogger("FlowerWatering")

class FlowerWatering(BfApp):
    name = "FlowerWatering"

    def on_start(self):
        pass

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        log.info("Turning pump ON t")
        self.publish("pump_control_msg", self.pump_control(True))
        time.sleep(int(self.config_get("pump_on_duration")))
        log.info("Turning pump OFF")
        self.publish("pump_control_msg", self.pump_control(False))

    def pump_control(self,state):
        msg = generate_msg_template(self.name,"command","binary","switch")
        msg["command"]["default"]["value"] = state
        return msg

