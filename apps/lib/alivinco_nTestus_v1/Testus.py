from blackflow.core.app import BfApp
from libs.iot_msg_lib.iot_msg import IotMsg, MsgType
import logging
log = logging.getLogger("Testus")


class Testus(BfApp):
    name = __name__

    def on_install(self):
        """
        Invoked once after app installation . Can be used to init application resources
        """
        log.info("%s app was installed "%self.name)

    def on_uninstall(self):
        """
        Invoked once before app uninstall  . Can be used to clean up application resources
        """
        log.info("%s app was uninstalled "%self.name)

    def on_start(self):
        """
           The method is invoked once during app startup . Init all variables here
        """
        log.info("%s app was started "%self.name)

    def on_stop(self):
        """
           The method is invoked during app shutdown . Do all cleanup work here
        """
        log.info("%s app was stopped "%self.name)

    def on_message(self, topic, iot_msg):
        """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
          :type topic: str
          :param topic: full topic name which includes prefix as "local:" , "mqtt:" , etc .
          :type iot_msg: libs.iot_msg_lib.iot_msg.IotMsg
          :param iot_msg: IotMsg object
         """
        log.info("%s app was triggered by %s" % (self.name, topic))
        situation = iot_msg.get_default_value()
        log.info("Alarm situation %s"%situation)
        # publish is a helper function for var_set.  First argument is publish destination alias and second is a payload
        siren_cmd = IotMsg(self.name,MsgType.CMD,msg_class="binary",msg_subclass="switch")
        self.publish("siren_control", siren_cmd)
        self.var_set("is_alarms_situation", True,persist=True)


