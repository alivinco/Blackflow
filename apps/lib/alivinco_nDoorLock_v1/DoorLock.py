import logging
from blackflow.libs.msg_template import generate_msg_template
from blackflow.core.app import BfApp

log = logging.getLogger("DoorLock")

class DoorLock(BfApp):
    name = __name__

    def on_start(self):
        pass

    def on_message(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        msg = self.var_get(triggered_by)
        if "command" in msg :
           default_value = msg["command"]["default"]["value"]
           self.publish("lock_control", self.lock_control(default_value))
        else :
           if msg["event"]["subtype"] == "lock":
               default_value = msg["event"]["default"]["value"]
               self.publish("switch_events", self.lock_event(default_value))
           elif msg["event"]["subtype"] == "inclusion_report":
               if msg["event"]["properties"]["inclusion_report"]["value"]["device"]["vendor"]=="0230":
                   node_id = msg["event"]["properties"]["inclusion_report"]["value"]["device"]["id"]
                   assoc_topic = "mqtt:/dev/zw/%s/dev_sys/1/commands"%node_id
                   self.var_set(assoc_topic,self.fix_assoc(node_id))

    def lock_control(self,state):
        msg = generate_msg_template(self.name,"command","binary","lock")
        msg["command"]["default"]["value"] = state
        msg["transport"] = "AES-128"
        return msg

    def lock_event(self,state):
        msg = generate_msg_template(self.name,"event","binary","switch")
        msg["event"]["default"]["value"] = state
        return msg

    def fix_assoc(self,node_id):
        msg = generate_msg_template(self.name,"command","association","set")
        msg["transport"] = "AES-128"
        msg["command"]["properties"] = {"group": {"value": 1},
                                        "devices": {"value": [1]} }
        return msg



