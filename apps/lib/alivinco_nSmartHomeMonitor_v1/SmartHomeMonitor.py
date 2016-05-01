from libs.iot_msg_lib.iot_msg import IotMsg, MsgType
from blackflow.core.app import BfApp
import time
import logging
log = logging.getLogger("SmartHomeMonitor")


class SmartHomeMonitor(BfApp):
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
        '''
          Building up sensor state list of sensors from list of subscribers .
          Some sensors may report Motion Detected only and some may report ON and OFF and will not report anything until there is constant motion in the room .
        '''
        self.last_activity_time = time.time()
        # sensor states
        self.devices_to_watch = []

        for key ,dev in self.get_subs().iteritems():
            if "motion" in key:
                role = "motion"
            elif "perimeter" in key:
                role = "perimeter"
            else:
                role = "other"
            self.devices_to_watch.append({"topic":dev["topic"], "state": False ,"role":role})
        # home / away / home_armed /
        self.mode = "home"

    def on_stop(self):
        """
           The method is invoked during app shutdown . Do all cleanup work here
        """
        log.info("%s app was stopped ")

    def on_message(self, topic, iot_msg):
        """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
         """
        log.info("%s app was triggered by %s" % (self.name, topic))
        situation = iot_msg.get_default_value()



        # publish is a helper function for var_set.  First argument is publish destination alias and second is a payload
        # self.publish("siren_control", self.siren_control("chime"))
        # self.publish("push_cmd_local", {"command": {"properties": {"title": "Emergency", "body": "Cord has been pulled or button pressed ", "address": ""}}})
        # self.var_set("is_alarms_situation", True)

    def is_motion_detected(self,motion_value,msg):
        """
        Motion sensor normalizer . Different sensors may report different values and some report OFF state and some ON state only
        :param topic:
        :param msg:
        :return:
        """
        return True if motion_value == 255 or motion_value == 1 else False

    def siren_control(self, state):
        # generate_msg_template function generates message template
        iot_msg = IotMsg(self.name,MsgType.CMD,msg_class="mode",msg_subclass="siren")
        iot_msg.set_default(state)
        return iot_msg
