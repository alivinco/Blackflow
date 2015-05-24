__author__ = 'alivinco'
from gevent.event import AsyncResult
import gevent

class Flow():

    def __init__(self,storage,flow_manager,id,name):
        self.flow_manager = flow_manager
        self.id = id
        self.name = name
        self.correlation_func = None
        self.trigger_topic = []
        self.receive_table = []
        self.receive_event = None
        self.storage = storage

    def flow(self,topic,msg):
        """
        Flow definition.Should be overriden
        :param topic: topic which has triggered the flow
        :param msg: payload of the message
        """
        # print "got message from door open sensor"+topic
        # print "sending let's wait for another message"
        # # msg = self._receive("/dev/zw/1/bin_motion/1/events",2000)
        # if msg:
        #     if msg["default"]["value"]:
        #         print "someone entered living area from outside"
        #         print "let's turn on lights"
        #         # msg = dmapi.binary_switch("ON")
        #         # self._send("/dev/zw/1/bin_switch/1/commands",msg)
        #
        #
        # else :
        #     print "nothing , just skipp end stop flow execution"



        print "Override me"

    def _receive(self,list_of_topics,timeout=30):
        """

        :param list_of_topics:
        :param timeout:
        :return:
        """
        self.receive_event = AsyncResult()
        self.receive_table = list_of_topics
        # flow manager has to  subscribe for the topic
        self.flow_manager.register_receive(list_of_topics)
        return self.receive_event.get(timeout)

    def inbox_put(self,topic,msg):
        """
        Method is invoked by Flow manager on new message
        :param topic:
        :param msg:
        """
        if topic in self.receive_table:
            self.receive_event.set({"topic":topic,"msg":msg})


    def _wait(self,timeout):
        gevent.sleep(timeout)

    def _send_sync(self,topic,msg_obj):
        result = ""
        return result

    def _send(self,topic,msg_obj):
        self.flow_manager.msg_transport.send(topic,msg_obj)




