import json
import logging
from smartlylib.service.Service import Service

__author__ = 'alivinco'

import libs.paho.mqtt.client as mqtt
log = logging.getLogger("bf_rules_runner")

class Adapter(Service):
    adapter = "test:"

    def __init__(self,context,name):
        self.context = context
        super(Adapter, self).__init__(name)

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

