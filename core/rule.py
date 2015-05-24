import logging

__author__ = 'alivinco'


"""
mqtt messages becomes key value pare
{"/dev/zw/75/bin_motion/1/events":{}}

"""

log = logging.getLogger("bf_rule")

class BfRule:
    name = "light_control"
    id = 3
    subscribe_for = ["/dev/zw/75/bin_motion/1/events","/dev/zw/45/sen_luminance/1/events"]
    schedule = "0 0 * * *"
    context = None

    def __init__(self):
        pass

    @classmethod
    def check(cls,triggered_by):
        # if cls.context.get("/dev/zw/75/bin_motion/1/events")["event"]["default"]["value"]==True and cls.context.get("home")["mode"]=="at_home":
        #     return True
        raise True

    def action(self):
        # self.publish("/dev/zw/75/bin_switch/1/commands","binary.switch",True)
        # self.context["lights_state"]=="off"
        raise NotImplementedError()







