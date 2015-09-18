import logging

__author__ = 'alivinco'


"""
mqtt messages becomes key value pare
{"/dev/zw/75/bin_motion/1/events":{}}



"""

log = logging.getLogger("bf_rule")

class BfApp:
    name = "app_name"
    context = None

    def __init__(self,app_config_id,alias,subscribes_for={},publishes_to={},configs={}):
        self.id = app_config_id
        # subscription bindings , it can be either local variables or generated by adapter
        self.sub_for = subscribes_for
        # publish binding . Similar to sub_for.
        self.pub_to = publishes_to
        self.configs = configs
        self.alias = alias

    def get_id(self):
        return self.id

    def on_start(self):
        """
        Invoked by app manager on app startup. Initialize app level variables here.
        """
        pass

    def on_stop(self):
        """
        Invoked by app manager on app shutdown. Destroy app level variables here.
        """
        pass

    def run(self,triggered_by):
        """
        The method is triggered by context change and is executed within it's own thread .
        :type triggered_by: variable name which has triggered app execution . If call was intiated by adapter it will
        be preffixed with adapter name , for instance mqtt:/dev/zw/87/mod_alarm/1/events
        """
        raise NotImplementedError()

    def var_set(self,name,value):
        self.context.set(name,value,self)

    def var_get(self,name):
        return self.context.get(name)

    def publish(self,name,value):
        self.var_set(self.pub_to[name]["topic"],value)

    def config_get(self,name):
        return self.configs[name]


