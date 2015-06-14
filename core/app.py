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
        # bindings
        self.sub_for = subscribes_for
        self.pub_to = publishes_to
        self.configs = configs
        self.alias = alias

    def get_id(self):
        return self.id

    def run(self,triggered_by):
        raise NotImplementedError()

    def var_set(self,name,value):
        self.context.set(name,value,self)

    def var_get(self,name):
        return self.context.get(name)




