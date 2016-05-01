from libs.iot_msg_lib.iot_msg import IotMsg, MsgType
from blackflow.core.app import BfApp
import logging
log = logging.getLogger("SceneController")


class SceneController(BfApp):
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
        it = self.config_get("inverted_topics")
        self.inverted_topics = it.split(";")
        log.info("Inverted topics %s"%self.inverted_topics)

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
        pubs = self.get_pubs()
        tmsg = IotMsg(self.name,MsgType.CMD,msg_class="binary",msg_subclass="switch")
        # message multiplexer
        for name,v in pubs.iteritems():
            if name in self.inverted_topics:
                tmsg.set_default(not iot_msg.get_default_value())
            else :
                tmsg.set_default(iot_msg.get_default_value())
            self.publish(name,tmsg)




