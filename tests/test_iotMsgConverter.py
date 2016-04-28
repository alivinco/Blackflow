import json
from unittest import TestCase

from libs.iot_msg_lib.iot_msg import MsgType, PayloadType, IotMsg
from libs.iot_msg_lib.iot_msg_converter import IotMsgConverter


class TestIotMsgConverter(TestCase):
    # def test_parse_topic(self):
    #     self.fail()
    #
    # def test_dict_to_iot_msg(self):
    #     self.fail()

    def test_string_to_iot_msg_v0(self):
        json_str = '{"origin": {"@id": "blackflow", "@type": "app"}, "event": {"default": {"value": true}, "subtype": "switch", "@type": "binary", "properties": {"p1": 165}}, "creation_time": 1459696245000, "uuid": "e48fbe58-3aaf-442d-b769-7a24aed8b716", "spid": "SP1"}'
        imsg = IotMsgConverter.string_to_iot_msg("/ta/zw/bin_switch/1/commands", json_str)
        self.assertEqual(imsg.get_msg_class(),"binary")
        self.assertEqual(imsg.get_msg_subclass(),"switch")
        self.assertEqual(imsg.get_type(),MsgType.EVT)
        self.assertEqual(imsg.get_properties()["p1"],165)
        self.assertEqual(imsg.get_uuid(),"e48fbe58-3aaf-442d-b769-7a24aed8b716")

    def test_string_to_iot_msg_v1(self):
        json_str = '{"msgType":"event","type": "binary","subType": "switch","default": {"value": true},"properties": {"p1": 165}, "creationTime": 1459696245000, "uuid": "e48fbe58-3aaf-442d-b769-7a24aed8b716", "id": "SP1"}'
        imsg = IotMsgConverter.string_to_iot_msg("jim1/evt/ta/zw/1/bin_switch/1", json_str)
        self.assertEqual(imsg.get_msg_class(),"binary")
        self.assertEqual(imsg.get_msg_subclass(),"switch")
        self.assertEqual(imsg.get_type(),MsgType.EVT)
        self.assertEqual(imsg.get_properties()["p1"],165)
        self.assertEqual(imsg.get_uuid(),"e48fbe58-3aaf-442d-b769-7a24aed8b716")

    # def test_iot_msg_to_dict(self):
    #     self.fail()
    #
    def test_iot_msg_to_str_v0(self):
        """
        Tests convertion from IotMsg object to json sting V0
        """
        m = IotMsg("test",MsgType.CMD,msg_class="binary",msg_subclass="switch",uuid_="e48fbe58-3aaf-442d-b769-7a24aed8b716")
        m.set_default(True)
        m.set_properties({"p1":165})
        mstr = IotMsgConverter.iot_msg_to_str(PayloadType.JSON_IOT_MSG_V0, m)
        self.assertIsInstance(mstr,basestring)
        jobj = json.loads(mstr)
        self.assertEqual(jobj["command"]["default"]["value"],True)
        self.assertEqual(jobj["command"]["@type"],"binary")
        self.assertEqual(jobj["command"]["subtype"],"switch")

    def test_iot_msg_to_str_v1(self):
        """
        Tests convertion from IotMsg object to json sting V1
        """
        m = IotMsg("test",MsgType.CMD,msg_class="binary",msg_subclass="switch",uuid_="e48fbe58-3aaf-442d-b769-7a24aed8b716")
        m.set_default(True)
        m.set_properties({"p1":165})
        mstr = IotMsgConverter.iot_msg_to_str(PayloadType.JSON_IOT_MSG_V1, m)
        self.assertIsInstance(mstr,basestring)
        jobj = json.loads(mstr)
        self.assertEqual(jobj["default"]["value"],True)
        self.assertEqual(jobj["msgType"],"command")
        self.assertEqual(jobj["type"],"binary")
        self.assertEqual(jobj["subType"],"switch")

    #
    def test_iot_msg_with_topic_to_str_v1(self):
        m = IotMsg("test",MsgType.CMD,msg_class="binary",msg_subclass="switch")
        m.set_default(True)
        m.set_properties({"p1":165})
        mstr = IotMsgConverter.iot_msg_with_topic_to_str("jim1/cmd/ta/zw/1/bin_switch/1", m)
        self.assertIsInstance(mstr,basestring)
        jobj = json.loads(mstr)
        self.assertEqual(jobj["default"]["value"],True)
        self.assertEqual(jobj["msgType"],"command")
        self.assertEqual(jobj["type"],"binary")
        self.assertEqual(jobj["subType"],"switch")
