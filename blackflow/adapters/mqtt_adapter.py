from blackflow.libs.iot_msg_lib.iot_msg_converter import IotMsgConverter

__author__ = 'alivinco'
import logging
from adapter import Adapter

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
        self.api_sub = ["/app/blackflow/%s/commands"%instance_name,"/discovery/commands"]
        self.api_pub = ["/app/blackflow/%s/events"%instance_name,"/discovery/events"]
        self.alias = "mqtt"

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
        elif topic in self.api_sub:
            log.info("Mqtt adapter subscribing for topic = %s" % topic)
            self.mqtt.subscribe(str(topic), qos=1)

    def unsubscribe(self, topic):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            log.info("Unsubscribing from topic = %s"%topic)
            self.mqtt.unsubscribe(str(topic))
        elif topic in self.api_sub:
            log.info("Mqtt adapter unsubscribing from topic = %s" % topic)
            self.mqtt.unsubscribe(str(topic))

    def on_message(self, client, userdata, msg):
        """
        On new message .
        :param client:
        :param userdata:
        :param msg:
        :return IotMsg
        """
        iot_msg = IotMsgConverter.string_to_iot_msg(msg.topic, msg.payload)
        if msg.topic in self.api_sub:
            try:
                self.api_handler.route(msg.topic, iot_msg)
            except Exception as ex:
                log.exception(ex)
        else:
            self.context.set(self.adapter_prefix + msg.topic, iot_msg, src_name=self, src_type="adapter")

    def publish(self, topic, iot_msg):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            self.mqtt.publish(topic, IotMsgConverter.iot_msg_with_topic_to_str(topic, iot_msg), qos=1)
        elif topic in self.api_pub:
            self.mqtt.publish(topic, IotMsgConverter.iot_msg_with_topic_to_str(topic, iot_msg), qos=1)

    def initialize(self):
        self.mqtt.connect(self.hostname, self.port)

    def stop(self):
        self.mqtt.disconnect()
        super(MqttAdapter, self).stop()

    def run(self):
        self.mqtt.loop_forever()
