__author__ = 'alivinco'
import json
import logging
from adapters.adapter import Adapter

import libs.paho.mqtt.client as mqtt
log = logging.getLogger("mqtt_adapter")

class MqttAdapter(Adapter):
    adapter_prefix = "mqtt:"
    def __init__(self,context,client_id="blackflow"):
        super(MqttAdapter, self).__init__(context,"MqttAdapter")
        self.mqtt = mqtt.Client(client_id=client_id, clean_session=True)
        self.mqtt.on_message = self.on_message
        self.hostname = "localhost"
        self.port = 1883

    def set_connection_params(self,hostname,port=1883):
        self.hostname = hostname
        self.port = port

    def subscribe(self,topic):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix,"")
            log.info("Mqtt adapter subscribing for topic = %s"%topic)
            # topic = topic.encode('ascii','ignore')
            self.mqtt.subscribe(str(topic),qos=1)

    def unsubscribe(self,topic):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix,"")
            self.mqtt.unsubscribe(topic)

    def on_message(self,client,userdata,msg):
        self.context.set(self.adapter_prefix + msg.topic, json.loads(msg.payload), src_name=self, src_type="adapter")

    def publish(self,topic,msg):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix,"")
            self.mqtt.publish(topic,json.dumps(msg),qos=1)

    def initialize(self):
        self.mqtt.connect(self.hostname,self.port)

    def stop(self):
        self.mqtt.disconnect()
        super(MqttAdapter, self).stop()

    def run(self):
        self.mqtt.loop_forever()


