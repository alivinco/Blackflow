from threading import Thread

__author__ = 'alivinco'


class Adapter(Thread):
    adapter = "test:"

    def __init__(self,context,name):
        super(Adapter, self).__init__(name = self.__class__.__name__)
        self.context = context
        self.context.add_adapter(self)

    def subscribe(self,topic):
        pass

    def unsubscribe(self,topic):
        pass

    def publish(self,topic,msg):
        pass

    def initialize(self):
        pass

    def stop(self):
        pass

    def run(self):
        pass

