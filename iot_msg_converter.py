import json
from iot_msg import PayloadType, IotMsg, MsgType
from iot_msg_codecs import IotMsgToJsonIotMsgV0Codec, IotMsgToJsonIotMsgV1Codec
import logging
__author__ = 'alivinco'

log = logging.getLogger("iot_msg_converter")


class IotMsgConverter:
    @staticmethod
    def parse_topic(topic):
        t = topic.split("/")
        if t[0] == "":
            t[0] = "jim0"
        return t

    @classmethod
    def dict_to_iot_msg(cls,topic, dict_msg, payload_type=None):
        """
        Converts dictionary into IotMessage object
        :type topic: string
        :param topic: origin topic
        :param dict_msg:
        :param payload_type:
        :return:
        """
        payload_type = payload_type if payload_type else PayloadType.str_to_type_map[cls.parse_topic(topic)[0]]
        if payload_type == PayloadType.JSON_IOT_MSG_V0:
            return IotMsgToJsonIotMsgV0Codec.decode(dict_msg)
        elif payload_type == PayloadType.JSON_IOT_MSG_V1:
            return IotMsgToJsonIotMsgV1Codec.decode(dict_msg)

    @classmethod
    def string_to_iot_msg(cls,topic, str_msg):
        """
        Converts json string into iot message
        :param topic:
        :param str_msg:
        :return:
        """
        payload_type = PayloadType.str_to_type_map[cls.parse_topic(topic)[0]]
        if payload_type in (PayloadType.JSON_IOT_MSG_V0, PayloadType.JSON_IOT_MSG_V1, PayloadType.JSON_OPAQUE):
            return cls.dict_to_iot_msg(topic, json.loads(str_msg), payload_type)

    @classmethod
    def iot_msg_to_dict(cls,payload_type, iot_msg):
        """
        Converts IoT message into dict which then can be serialized into JSON string
        :param payload_type:
        :param iot_msg:
        :return:
        """
        if payload_type == PayloadType.JSON_IOT_MSG_V0:
            return IotMsgToJsonIotMsgV0Codec.encode(iot_msg)
        elif payload_type == PayloadType.JSON_IOT_MSG_V1:
            return IotMsgToJsonIotMsgV1Codec.encode(iot_msg)

    @classmethod
    def iot_msg_to_str(cls,payload_type, iot_msg):
        """
        Converts IoT message into JSON string .
        :type payload_type: PayloadType
        :param payload_type:
        :param iot_msg:
        :return:
        """
        return json.dumps(cls.iot_msg_to_dict(payload_type, iot_msg))

    @classmethod
    def iot_msg_with_topic_to_str(cls,topic, iot_msg):
        """
        Converts IoT message into JSON string . The same as iot_msg_to_str but takes topic insted of PayloadType
        :param topic:
        :param iot_msg:
        :return:
        """
        payload_type = PayloadType.str_to_type_map[cls.parse_topic(topic)[0]]
        log.debug("payload type = %s"%payload_type)
        return IotMsgConverter.iot_msg_to_str(payload_type, iot_msg)