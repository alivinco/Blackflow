import logging
from libs.msg_template import generate_msg_template
from core.app import BfApp

log = logging.getLogger("SchedulerTest")

class SchedulerTest(BfApp):
     name = __name__

     def on_start(self):
        """
           The method is invoked once during app startup . Init all variables here
        """
        pass

     def on_stop(self):
        """
           The method is invoked during app shutdown . Do all cleanup work here
        """
        pass

     def on_message(self,triggered_by):
         """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
         """
         log.info("%s app was triggered by %s"%(self.name,triggered_by))
         #self.publish("push_notif_msg",{"command":{"properties":{"title":"Emergency cancel","body":"Everything is ok","address":""}}})
         
    