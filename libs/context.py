from Queue import Queue, Empty
import json
import logging
import os
from threading import Lock
import time

__author__ = 'alivinco'
log = logging.getLogger("context")

class BfContext:
    def __init__(self):
        self.context = {}
        self.write_lock = Lock()
        self.adapters = []

    def on_context_change(self,var_name):
        """
        The method should be overriden
        :param var_name:
        """
        pass

    def add_adapter(self,adapter_inst):
        self.adapters.append(adapter_inst)
        log.info("Adapter %s was added to context"%adapter_inst.name)

    def adapter_sync(self,var_name,value):
        # loops through all adapters and pass var_to
        for adapter in self.adapters:
            if adapter.adapter_prefix in var_name:
                adapter.publish(var_name,value)

    def set(self, key, value, src_name=None, src_type="app"):
        """
        Context value setter
        :param key: unique key
        :param value: value
        :param src_name: reference to class which did the modification .
        :param src_type: param is needed to prevent infinite loops .
        """
        log.info("Context change key=%s , value=%s , mod_by=%s"%(key,value,src_name.name if src_name else ""))
        with self.write_lock:
            self.context[key] = {"value":value,"src_name":src_name.name if src_name else None,"src_type":src_type,"timestamp":time.time()}
            self.on_context_change(key)
            if src_type == "app":
                self.adapter_sync(key,value)

    def get(self,key):
        try:
            return self.context[key]["value"]
        except:
            return None

    def get_time_since_last_update(self,key):
        """
        Return time elapsed time since last variable update .
        :param key:
        :return: seconds as floating point since last update
        """
        if key in self.context:
            start_time = self.context[key]["timestamp"]
        else :
            start_time = 0
        return time.time() - start_time

    def get_dict(self):
            return self.context