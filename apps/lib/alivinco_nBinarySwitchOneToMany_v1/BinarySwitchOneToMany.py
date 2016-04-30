import logging
from blackflow.core.app import BfApp
from libs.iot_msg_lib.iot_msg import IotMsg, MsgType
log = logging.getLogger("BinarySwitchOneToMany")


class BinarySwitchOneToMany(BfApp):
    name = __name__

    def on_message(self, topic, iot_msg):
        """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
         """
        log.info("%s app was triggered by %s" % (self.name, topic))
        pubs = self.get_pubs()
        tmsg = IotMsg(self.name,MsgType.CMD,msg_class="binary",msg_subclass="switch")
        tmsg.set_default(iot_msg.get_default_value())
        # message multiplexer
        for name,v in pubs.iteritems():
            self.publish(name,tmsg)