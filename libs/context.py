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

    def on_context_change(self,var_name):
        pass

    def set(self,key,value,mod_by=None):
        """
        Context value setter
        :param key: unique key
        :param value: value
        :param mod_by: reference to class which did the modification .
        """
        log.info("Context change key=%s , value=%s , mod_by=%s"%(key,value,mod_by.name if mod_by else ""))
        with self.write_lock:
            self.context[key] = {"value":value,"mod_by":mod_by.name if mod_by else None,"timestamp":time.time()}
            self.on_context_change(key)

    def get(self,key):
        return self.context[key]["value"]
