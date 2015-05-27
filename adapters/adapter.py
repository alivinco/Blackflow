import json
import logging
from smartlylib.service.Service import Service

__author__ = 'alivinco'

import libs.paho.mqtt.client as mqtt
log = logging.getLogger("bf_rules_runner")

class Adapter(Service):
    adapter = "test:"

    def __init__(self,context,name):
        super(Adapter, self).__init__(name)
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

