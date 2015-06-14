__author__ = 'alivinco'
import uuid
import time

def generate_msg_template(app_name, msg_type, msg_class, msg_subclass):
    return {"origin": {"@id": app_name, "@type": "app"},
            "uuid": str(uuid.uuid4()),
            "creation_time": int(time.time()) * 1000,
            msg_type: {"default": {"value": ""}, "subtype": msg_subclass, "@type": msg_class},
            "spid": "SP1",
            "@context": "http://context.smartly.no"
            }
