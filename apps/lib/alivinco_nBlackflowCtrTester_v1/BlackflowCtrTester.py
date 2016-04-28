from blackflow.libs.msg_template import generate_msg_template
from blackflow.core.app import BfApp
import logging
log = logging.getLogger("BlackflowCtrTester")


class BlackflowCtrTester(BfApp):
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
        self.counter = 1 
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
        # publish is a helper function for var_set.  First argument is publish destination alias and second is a payload
        self.counter += 1
        self.var_set("test_var", self.counter )

    
