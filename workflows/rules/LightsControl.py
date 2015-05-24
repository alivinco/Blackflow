import logging
from core.rule import BfRule

__author__ = 'alivinco'


"""
mqtt messages becomes key value pare
{"/dev/zw/75/bin_motion/1/events":{}}

"""
log = logging.getLogger("LightsControl")

class LightsControl(BfRule):

    name = "light_control"
    id = 3
    subscribe_for = ["mqtt:/dev/zw/75/bin_motion/1/events","mqtt:/dev/zw/45/sen_luminance/1/events"]
    schedule = "0 0 * * *"

    @staticmethod
    def check(self,triggered_by):
        log.info("Doing check of %s"%triggered_by)
        if triggered_by == "mqtt:/dev/zw/75/bin_motion/1/events":
            if self.context.get("mqtt:/dev/zw/75/bin_motion/1/events")["event"]["default"]["value"]==True and self.context.get("home")["mode"]=="at_home":
                return True
        return False

    def action(self):
        # self.publish("/dev/zw/75/bin_switch/1/commands","binary.switch",True)
        log.info("Actionnnn")
        self.context.set("lights_state","off",self)
        self.context.set("mqtt:/dev/app/LightsControl/event",{"status":"off"},self)




