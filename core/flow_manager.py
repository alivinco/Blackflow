__author__ = 'alivinco'

import threading
import importlib

class ContextStorage():
    def __init__(self):
        self.storage = []
        self.lock = threading.Lock

    def add(self,key,value,flow_name="",flow_instance_id=-1):
        with self.lock:
            if key in self.storage:
                return False
            else :
                self.storage.append({"key":key,"value":value,"flow_name":flow_name,"flow_instance_id":flow_instance_id})
                return True

    def get(self,key,flow_name="",flow_instance_id=-1):
        with self.lock:
            try:
                return self.storage[key]
            except:
                return None




# class FlowInstance():
#     def __init__(self,id,name,trigger_topics,msg_type,correlation_func_ref):
#         self.id = name
#         self.name =  name
#         self.trigger_topics = trigger_topics
#         self.msg_type = msg_type
#         self.correlation_func = correlation_func_ref
#         # states are "running","receive","waiting","sending"
#         self.state = ""
#         self.receive_topics = []
#         self.receive_event = None

# The class is singleton and is responsible for creation and tracking instances
class FlowManager():


    def __init__(self,msg_transport):
        # Table contains flow metadata
        self.flow_table = []
        # Table contains all active flow instances
        self.instance_table = []
        self.msg_transport = msg_transport
        # context is key-value store , which can be used by flows to persist data
        self.context = ContextStorage()

    def register_flow(self,flow_name,package,list_of_trigger_topics):
        """
        Registering flow definitions by loading module and creating flow class instance and assigning triggering topics
        :param flow_name:
        :param list_of_trigger_topics:
        """
        module = importlib.import_module(flow_name,package)
        flow_inst = module()
        flow_inst.name = flow_name
        flow_inst.trigger_topic = list_of_trigger_topics
        self.instance_table.append(flow_inst)

    def register_receive(self,list_of_topics):
        for topic in list_of_topics:
            self.msg_transport.subscribe(topic)

    def _on_message(self,topic,payload):
        for f_instance in self.instance_table:
            if topic in f_instance.receive_table:
                f_instance.inbox_put(topic,payload)

