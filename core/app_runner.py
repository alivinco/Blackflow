from Queue import Queue, Empty
import importlib
import json
import logging, logging.config
import os
from threading import Thread
import threading
import configs.log
from libs.thread_pool import ThreadPool
from smartlylib.service.Service import ServiceRunner, Service

__author__ = 'alivinco'

log = logging.getLogger("bf_apps_runner")


class AppRunner(Service):
    def __init__(self, context,adapters):
        # threading.Thread.__init__ (self)
        super(AppRunner, self).__init__(self.__class__.__name__)
        self.apps = []
        self.context_change_queue = Queue()
        self.is_running = True
        self.app_execution_thread_pool = ThreadPool(5)
        context.on_context_change = self.on_context_change
        self.context = context
        self.apps_dir_path = "apps"
        self.adapters = adapters


    def initialize(self):
        log.info("***Initializing apps runner service....")
        self.apps = []
        self.load_apps()

    def on_context_change(self, var_name):
        """
        THe method should be called by context whenever context variable is changed
        :param var_name: variable name
        """
        self.context_change_queue.put(var_name)

    def check_if_app_is_memory(self,config_id):
        return True if len(filter(lambda ap:ap.id==config_id,self.apps)) else False

    def load_app(self,app_config):
        if self.check_if_app_is_memory(app_config["id"]):
            log.info("App is already in memory . Reloading....")
            reload("apps.lib." + app_config["name"])
            self.apps.remove(filter(lambda ap:ap.id==app_config["id"],self.apps)[0])
        else :
            imp_mod = importlib.import_module("apps.lib." + app_config["name"])
            app_class = getattr(imp_mod, app_config["name"])
            app_class.context = self.context

        app_inst = app_class(app_config["id"],app_config["alias"],app_config["sub_for"],app_config["pub_to"],app_config["configs"])
        log.info("Apps with id = %s , name = %s , alias = %s was loaded."%(app_inst.id,app_inst.name,app_inst.alias))

        # setting up subscriptions in adapters
        for key,subsc in app_inst.sub_for.iteritems():
            for adapter in self.adapters:
                 adapter.subscribe(subsc)

        self.apps.append(app_inst)

    def load_apps(self):
        log.info("Loading apps ")
        apps_reg = json.load(file(os.path.join(self.apps_dir_path, "apps.json")))
        for app_config in apps_reg:
            self.load_app(app_config)

    def run(self):
        while not self.isStopped():
            try:
                change_var_name = self.context_change_queue.get(timeout=10)
            except Empty:
                continue
            for app in self.apps:
                if change_var_name in app.sub_for.values():
                    try:
                            log.debug("Adding task to the queue for app = %s" % app.alias)
                            self.app_execution_thread_pool.add_task(app.run,change_var_name)
                    except Exception as ex:
                        log.debug("App check method has failed with exception:")
                        log.exception(ex)
        log.info("Apps runner main loop stopped.")
