from blackflow.libs.msg_template import generate_msg_template
from blackflow.core.app import BfApp
import logging
log = logging.getLogger("BfApplicationTemplate")


class BfApplicationTemplate(BfApp):
    name = __name__

    def on_install(self):
        """
        Invoked once after app installation . Can be used to init application resources
        """
        log.info("%s app was installed ")

    def on_uninstall(self):
        """
        Invoked once before app uninstall  . Can be used to clean up application resources
        """
        log.info("%s app was uninstalled ")

    def on_start(self):
        """
           The method is invoked once during app startup . Init all variables here
        """
        log.info("%s app was started ")

    def on_stop(self):
        """
           The method is invoked during app shutdown . Do all cleanup work here
        """
        log.info("%s app was stopped ")

    def on_message(self, topic, msg):
        """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
         """
        log.info("%s app was triggered by %s" % (self.name, topic))
        situation = msg["event"]["default"]["value"]
        # publish is a helper function for var_set.  First argument is publish destination alias and second is a payload
        self.publish("siren_control", self.siren_control("chime"))
        self.publish("push_cmd_local", {"command": {"properties": {"title": "Emergency", "body": "Cord has been pulled or button pressed ", "address": ""}}})
        self.var_set("is_alarms_situation", True)

    def siren_control(self, state):
        # generate_msg_template function generates message template
        msg = generate_msg_template(self.name, "command", "mode", "siren")
        msg["command"]["default"]["value"] = state
        return msg
