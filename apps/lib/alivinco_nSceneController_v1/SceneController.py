from blackflow.libs.msg_template import generate_msg_template
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
            if name in self.inverted_topics:
                tmsg["command"]["default"]["value"] = not msg["event"]["default"]["value"]
            self.publish(name,tmsg)




