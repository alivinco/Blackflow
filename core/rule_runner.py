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

log = logging.getLogger("bf_rules_runner")


class RuleRunner(Service):
    def __init__(self, context,adapters):
        # threading.Thread.__init__ (self)
        super(RuleRunner, self).__init__(self.__class__.__name__)
        self.rules = []
        self.context_change_queue = Queue()
        self.is_running = True
        self.rule_execution_thread_pool = ThreadPool(5)
        context.on_context_change = self.on_context_change
        self.context = context
        self.rules_dir_path = "workflows"
        self.adapters = adapters

    def initialize(self):
        log.info("***Initializing rule runner service....")
        self.rules = []
        self.load_rules()

    def on_context_change(self, var_name):
        """
        THe method should be called by context whenever context variable is changed
        :param var_name: variable name
        """
        # loops through all adapters and pass var_to
        for adapter in self.adapters:
            if adapter.adapter_prefix in var_name:
                adapter.publish(var_name,self.context.get(var_name))

        self.context_change_queue.put(var_name)

    def load_rules(self):
        log.info("Loading rules ")
        rules_reg = json.load(file(os.path.join(self.rules_dir_path, "rules.json")))

        for rule in rules_reg:
            # path = os.path.join(self.rules_dir_path,rule["class"])
            # loaded_mod = __import__(path+"."+mod_nasme, fromlist=[mod_name])
            # Get the class's name
            imp_mod = importlib.import_module("workflows.rules." + rule["class"])
            rule_class = getattr(imp_mod, rule["class"])
            rule_class.context = self.context
            log.info("Rule " + str(rule_class) + " loaded")
            # setting up subscriptions in adapters
            for subsc in rule_class.subscribe_for:
                for adapter in self.adapters:
                    adapter.subscribe(subsc)

            self.rules.append(rule_class)
            # Load it from imported module

    def run(self):
        while not self.isStopped():
            try:
                change_var_name = self.context_change_queue.get(timeout=10)
            except Empty:
                continue
            for rule in self.rules:
                if change_var_name in rule.subscribe_for:
                    try:
                        if rule.check(rule, change_var_name):
                            # creating rule instance and starting action in separate thread
                            rule_instance = rule()
                            log.debug("Adding task to the queue %s" % rule.name)
                            self.rule_execution_thread_pool.add_task(rule_instance.action)
                    except Exception as ex:
                        log.debug("Rule check has failed with exception")
                        log.exception(ex)
        log.info("Rule runner main loop stoped.")
