__author__ = 'alivinco'



class FlowInstance():
    def __init__(self,id,name,trigger_topic,msg_type):
        self.id = id
        self.name =  name
        self.trigger_topic = trigger_topic
        self.msg_type = msg_type

    def get_msg_from_cache(self,key):
        return ""

class FlowController():
    # Table contains flow metadata
    flow_table = {}
    # Table contains all active flow instances
    instance_table = []


    def __init__(self):
        pass

    def on_message(self,topic,payload):
        pass

    # def