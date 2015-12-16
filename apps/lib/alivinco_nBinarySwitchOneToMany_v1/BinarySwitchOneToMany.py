from blackflow.libs.msg_template import generate_msg_template
from blackflow.core.app import BfApp
import logging
log = logging.getLogger("BinarySwitchOneToMany")


class BinarySwitchOneToMany(BfApp):
    name = __name__

    def on_message(self, topic, msg):
        """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
         """
        log.info("%s app was triggered by %s" % (self.name, topic))
        pubs = self.get_pubs()
        tmsg = generate_msg_template(self.name, "command", "binary", "switch")
        tmsg["command"]["default"]["value"] = msg["event"]["default"]["value"]
        # message multiplexer
        for name,v in pubs.iteritems():
            self.publish(name,tmsg)
        