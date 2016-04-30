# import json
# import uuid
# import time
#
# __author__ = 'alivinco'
#
#
# def generate_msg_template(app_name, msg_type, msg_class, msg_subclass, request_msg=None):
#     msg = {"origin": {"@id": app_name, "@type": "app"},
#            "uuid": str(uuid.uuid4()),
#            "creation_time": int(time.time()) * 1000,
#            msg_type: {"default": {"value": ""}, "subtype": msg_subclass, "@type": msg_class, "properties": {}},
#            "spid": "SP1"
#            }
#     if request_msg:
#         msg["corid"] = request_msg["uuid"]
#     return msg
#
#
# class IotMsg:
#     def __init__(self, app_name):
#         self.__app_name = app_name
#         self.__msg = {}
#         self.__msg_type = None
#
#     @staticmethod
#     def new_iot_msg_from_dict(app_name, dict_msg):
#         """
#         Factory method . Creates IotMsg object out of dict
#         :param app_name: application name
#         :param json_msg: message in form of json dictionary
#         :return: returns IotMsg object
#         """
#         m = IotMsg(app_name)
#         m.init_from_dict(dict_msg)
#         return m
#
#     @staticmethod
#     def new_iot_msg_from_json(app_name, json_msg):
#         return IotMsg.new_iot_msg_from_dict(app_name, json.loads(json_msg))
#
#     @staticmethod
#     def new_iot_msg(app_name, msg_type, msg_class, msg_subclass, request_msg=None):
#         """
#         Factory. Creates IotMsg object using basic parameters .
#         :param app_name: application name
#         :param msg_type: msg type , command / event
#         :param msg_class: msg class or msg type , for instance binary , level , sensor , etc .
#         :param msg_subclass: msg subclass . for instance switch , thermostat , temperature , etc .
#         :param request_msg: request message if new message is meant to be response message
#         :return: IotMsg
#         """
#         m = IotMsg(app_name)
#         m.init_from_params(msg_type, msg_class, msg_subclass)
#         return m
#
#     def init_from_params(self, msg_type, msg_class, msg_subclass, request_msg=None):
#         self.__msg = {"origin": {"@id": self.__app_name, "@type": "app"},
#                "uuid": str(uuid.uuid4()),
#                "creation_time": int(time.time()) * 1000,
#                msg_type: {"default": {"value": ""}, "subtype": msg_subclass, "@type": msg_class, "properties": {}},
#                "spid": "SP1"
#                }
#         self.__msg_type = msg_type
#         if request_msg:
#             self.__msg["corid"] = request_msg["uuid"]
#
#     def init_from_dict(self, json_msg):
#         """
#
#         :param json_msg:
#         """
#         self.__msg = json_msg
#         if "command" in self.__msg:
#             self.__msg_type = "command"
#         else :
#             self.__msg_type = "event"
#
#     def get_uuid(self):
#         return self.__msg["uuid"]
#
#     def set_corr_id_from_raw_request_dict(self,request_msg):
#         """
#
#         :param request_msg:
#         """
#         self.__msg["corid"] = request_msg["uuid"]
#
#     def set_corr_id_from_iotmsg(self,iot_msg):
#         """
#
#         :param request_msg:
#         """
#         self.__msg["corid"] = iot_msg.get_uuid()
#
#     def set_default(self, value, unit=None, type_=None):
#         """
#
#         :param value:
#         :param unit:
#         :param type_:
#         """
#         v = {"value":value}
#         if unit:
#             v["unit"] = unit
#         if type_ :
#             v["type"] = type_
#
#         self.__msg[self.__msg_type]["default"] = v
#
#     def get_default(self):
#         return self.__msg[self.__msg_type]["default"]
#
#     def get_default_value(self):
#          return self.__msg[self.__msg_type]["default"]["value"]
#
#     def set_properties(self, props):
#         self.__msg[self.__msg_type]["properties"] = props
#
#     def get_properties(self):
#         return self.__msg[self.__msg_type]["properties"]
#
#     def get_dict(self):
#         return self.__msg
#
#     def get_json(self):
#         return json.dumps(self.__msg)
#
#     def get_msg_class(self):
#         return self.__msg[self.__msg_type]["@type"]
#
#     def get_msg_subclass(self):
#         return self.__msg[self.__msg_type]["subtype"]
#
#
# if __name__ == '__main__':
#     m = IotMsg.new_iot_msg("blackflow", "command", "binary", "switch")
#     m.set_default(True)
#     m.set_properties({"p1":165})
#     print json.dumps(m.get_dict())
#     json_str = '{"origin": {"@id": "blackflow", "@type": "app"}, "event": {"default": {"value": true}, "subtype": "switch", "@type": "binary", "properties": {"p1": 165}}, "creation_time": 1459696245000, "uuid": "e48fbe58-3aaf-442d-b769-7a24aed8b716", "spid": "SP1"}'
#     m2 = IotMsg.new_iot_msg_from_dict("blackflow", json.loads(json_str))
#     print m2.get_default()["value"]
#     print m2.get_properties()
#     print m2.get_msg_class()
#     print m2.get_msg_subclass()
