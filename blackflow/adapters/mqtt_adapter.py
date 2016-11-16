from blackflow.libs.iot_msg_lib.iot_msg_converter import IotMsgConverter
import threading
from adapter import Adapter
import paho.mqtt.client as mqtt
from blackflow.libs import logger
__author__ = 'alivinco'
log = logger.getLogger("mqtt_adapter")


class MqttAdapter(Adapter):
    adapter_prefix = "mqtt:"

    def __init__(self, context,instance_name, client_id="blackflow",host="localhost",port=1883,username="",password="",use_clean_session=True):
        super(MqttAdapter, self).__init__(context, "MqttAdapter")
        self.mqtt = mqtt.Client(client_id=client_id, clean_session=use_clean_session)
        self.mqtt.on_message = self.on_message
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_disconnect = self.on_disconnect
        if username:
            self.mqtt.username_pw_set(username,password)
        self.hostname = host
        self.port = port
        self.api_handler = None
        self.api_sub = ["jim1/cmd/app/blackflow/%s"%instance_name,"jim1/cmd/discovery"]
        self.api_pub = ["jim1/evt/app/blackflow/%s"%instance_name,"jim1/evt/discovery"]
        self.alias = "mqtt"
        self.startup_event = threading.Event()
        self.global_prefix = ""
        self.use_clean_session = use_clean_session
        self.topics = list()

    def set_global_prefix(self,prefix):
        self.global_prefix = prefix

    def set_connection_params(self, hostname, port=1883):
        self.hostname = hostname
        self.port = port

    def set_api_handler(self, api_handler):
        self.api_handler = api_handler

    def subscribe(self, topic):
        self.topics.append(topic)
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            if self.global_prefix:
                topic = self.global_prefix+"/"+topic
            log.info("Mqtt adapter subscribing for topic = %s" % topic)
            self.mqtt.subscribe(str(topic), qos=1)
        elif topic in self.api_sub:
            if self.global_prefix:
                topic = self.global_prefix+"/"+topic
            log.info("Mqtt adapter subscribing for topic = %s" % topic)
            self.mqtt.subscribe(str(topic), qos=1)
        else :
            log.info("Subscribe operation for topic = %s is skipped "%topic)

    def unsubscribe(self, topic):
        self.topics.remove(topic)
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            if self.global_prefix:
                topic = self.global_prefix+"/"+topic
            log.info("Unsubscribing from topic = %s"%topic)
            self.mqtt.unsubscribe(str(topic))
        elif topic in self.api_sub:
            if self.global_prefix:
                topic = self.global_prefix+"/"+topic
            log.info("Mqtt adapter unsubscribing from topic = %s" % topic)
            self.mqtt.unsubscribe(str(topic))

    def on_connect(self,client, userdata, flags, rc):
        log.info("Mqtt adapter connected %s , %s , %s"%(client,userdata,flags))
        self.startup_event.set()
        for topic in list(self.topics):
            self.subscribe(topic)

    def on_disconnect(self,client, userdata, rc):
        log.error("Connection to mqtt broker was lost.")

    def on_message(self, client, userdata, msg):
        """
        On new message .
        :param client:
        :param userdata:
        :param msg:
        :return IotMsg
        """
        try:
            if self.global_prefix:
                msg.topic = msg.topic.replace(self.global_prefix+"/","")
            log.debug("New msg from topic %s"%msg.topic)
            iot_msg = IotMsgConverter.string_to_iot_msg(msg.topic, msg.payload)
            if msg.topic in self.api_sub:
                try:
                    self.api_handler.route(msg.topic, iot_msg)
                except Exception as ex:
                    log.exception(ex)
            else:
                self.context.set(self.adapter_prefix + msg.topic, iot_msg, src_name=self, src_type="adapter")

        except Exception as ex:
            log.exception(ex)

    def publish(self, topic, iot_msg):
        if self.adapter_prefix in topic:
            topic = topic.replace(self.adapter_prefix, "")
            final_topic = self.global_prefix+"/"+topic if self.global_prefix else topic
            self.mqtt.publish(final_topic, IotMsgConverter.iot_msg_with_topic_to_str(topic, iot_msg), qos=0)
        elif topic in self.api_pub:
            final_topic = self.global_prefix+"/"+topic if self.global_prefix else topic
            self.mqtt.publish(final_topic, IotMsgConverter.iot_msg_with_topic_to_str(topic, iot_msg), qos=0)

    def initialize(self):
        self.mqtt.connect(self.hostname, self.port)
        log.info("Adapter init is completed")

    def stop(self):
        log.info("Stopping MQTT adapter.")
        self.mqtt.disconnect()
        self.startup_event.clear()
        super(MqttAdapter, self).stop()

    def start(self):
        log.info("Starting MQTT adapter.")
        self.initialize()
        super(MqttAdapter, self).start()
        # waiting while connection is established
        self.startup_event.wait(10)

    def run(self):
        try:
            log.info("Starting loop")
            self.mqtt.loop_forever()
            log.info("Mqtt loop is stopped.")
        except Exception as ex:
            log.error(ex)
