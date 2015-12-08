import logging
from blackflow.core.app import BfApp

log = logging.getLogger(__name__)

class AlarmApp(BfApp):
    name = __name__

    def on_start(self):
        """


        """

        log.info("Initializing alarm app")

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        trigger_value = self.var_get(triggered_by)["command"]["default"]["value"]
        elapsed_time = self.context.get_time_since_last_update("local:alarm_state")
        if trigger_value:
            if self.var_get("alarm_state")=="armed":
               self.notify(triggered_by)
            elif self.var_get("alarm_state")=="alarm" and self.config_get("local:alarm_state_timeout")<elapsed_time:
               self.notify(triggered_by)
        elif self.config_get("alarm_state_timeout")<elapsed_time:
            self.var_set("local:alarm_state", "armed" )


    def notify(self,description):
        self.var_set("alarm_state", "alarm" )
        self.var_set("push_notification",
                             {"command":{"properties":
                                             {"title":"Alarm",
                                              "body":"Triggered by %s"%description,
                                              "address":None}}})



