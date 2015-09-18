__author__ = 'alivinco'
import json
import logging
from adapters.adapter import Adapter

import paho.mqtt.client as mqtt

log = logging.getLogger("mqtt_adapter")


class MqttAdapter(Adapter):
    adapter_prefix = "mqtt:"

    def __init__(self, context,instance_name, client_id="blackflow",host="localhost",port=1883):
        super(MqttAdapter, self).__init__(context, "MqttAdapter")
        self.mqtt = mqtt.Client(client_id=client_id, clean_session=True)
        self.mqtt.on_message = self.on_message
        self.hostname = host
        self.port = port
        self.api_handler = None
        self.api_sub = "/app/blackflow/%s/commands"%instance_name
        self.api_pub = "/app/blackflow/%s/events"%instance_name

    def set_connection_params(self, hostname, port=1883):
        self.hostname = hostname
        self.port = port

    def set_api_handler(self, api_handler):
        self.api_handler = api_handler

    def subscribe(self, topic):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            log.info("Mqtt adapter subscribing for topic = %s" % topic)
            self.mqtt.subscribe(str(topic), qos=1)
        elif self.api_sub == topic:
            log.info("Mqtt adapter subscribing for topic = %s" % topic)
            self.mqtt.subscribe(str(topic), qos=1)

    def unsubscribe(self, topic):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            self.mqtt.unsubscribe(str(topic))

    def on_message(self, client, userdata, msg):
        jmsg = json.loads(msg.payload)
        if self.api_sub == msg.topic:
            try:
                self.api_handler.route(msg.topic, jmsg)
            except Exception as ex:
                log.exception(ex)
        else:
            self.context.set(self.adapter_prefix + msg.topic, jmsg, src_name=self, src_type="adapter")

    def publish(self, topic, msg):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            self.mqtt.publish(topic, json.dumps(msg), qos=1)
        elif self.api_pub == topic:
            self.mqtt.publish(topic, json.dumps(msg), qos=1)

    def initialize(self):
        self.mqtt.connect(self.hostname, self.port)

    def stop(self):
        self.mqtt.disconnect()
        super(MqttAdapter, self).stop()

    def run(self):
        self.mqtt.loop_forever()