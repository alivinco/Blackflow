import pickle
import threading
from Queue import Queue, Empty
import json
import logging
import os
from threading import Lock
import time

import sqlite3

from blackflow.libs.analytics import AppAnalytics

__author__ = 'alivinco'
log = logging.getLogger("context")


class BfContext:
    def __init__(self, storage_path=None):
        self.context = {}
        self.write_lock = Lock()
        self.adapters = []
        self.analytics = AppAnalytics()
        # Persistent var storage
        self.db_storage_path = storage_path
        self.db_lock = threading.Lock()
        self.db_conn = None
        if storage_path:
            self.connect_db(self.db_storage_path)
            self.init_db()
            self.load_context_from_storage()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def connect_db(self,db_file_path):
        log.info("Connecting to database file : %s"%str(db_file_path))
        self.db_conn = sqlite3.connect(db_file_path, check_same_thread=False)
        log.info("Connected")

    def init_db(self):
        # check if tables exists , if not create one
        var_storage_table = "create table if not exists var_storage (var_key text PRIMARY KEY,var_value text ,src_name TEXT,src_type TEXT,updated REAL )"
        self.db_conn.execute(var_storage_table)

    def load_context_from_storage(self):
        with self.db_lock:
            c = self.db_conn.cursor()
            iter = c.execute("select var_key,var_value,src_name,src_type,updated from var_storage")
            for item in iter:
                self.context[item[0]] = {"value": self._deserialize_var(item[1]),
                                         "src_name": item[2] if item[2] else None,
                                         "src_type": item[3],
                                         "timestamp": item[4],
                                         "persisted": True}
            c.close()

    def cleanup(self):
        if self.db_conn:
            self.db_conn.close()

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

    def set(self, key, value, src_name=None, src_type="app", persist=False):
        """
        Context value setter
        :param key: unique key , which in some cases is destination address .
        :param value: value
        :param src_name: reference to class which did the modification .
        :param src_type: param is needed to prevent infinite loops .
        :param persist: Defines if variable should be persisted to local storage or reside only in memory
        :param persist: bool
        """
        log.info("Context change key=%s , value=%s , mod_by=%s"%(key, value, src_name.alias if src_name else ""))
        with self.write_lock:
            self.context[key] = {"value":value,"src_name":src_name.alias if src_name else None,"src_type":src_type,"timestamp":time.time(),"persisted":persist}
            if persist:
                self._persist_variable(key, self.context[key])
            if src_name:
                self.analytics.tick_link_counter(src_name.alias, key)
            self.on_context_change(key)
            if src_type == "app":
                self.adapter_sync(key, value)

    def _serialize_var(self,var):
        return pickle.dumps(var)

    def _deserialize_var(self,var):
        return pickle.loads(var)

    def _persist_variable(self, key, value):
        if self.db_conn:
            with self.db_lock:
                self.db_conn.execute("INSERT or REPLACE INTO var_storage(var_key,var_value,src_name,src_type,updated) VALUES (?,?,?,?,?)",
                                     (key, self._serialize_var(value["value"]), value["src_name"], value["src_type"], value["timestamp"]))
                self.db_conn.commit()

    def get(self, key):
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