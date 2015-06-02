__author__ = 'alivinco'
import importlib
import json
import os
import logging

log = logging.getLogger("bf_app_manager")

class AppManager():
    def __init__(self,context,adapters):
        self.configured_app_instances = []
        self.app_classes = {}
        self.app_defs = None
        self.app_configs = None
        self.apps_dir_path = "apps"
        self.load_definitions()
        self.context = context
        self.adapters = adapters
        self.load_app_classes()
        self.configure_and_init_app_instance()
        log.info("App init process completed. %s apps were initialized and configured "%len(self.configured_app_instances))

    def initialize(self):
        pass

    def load_definitions(self):
        self.app_defs = json.load(file(os.path.join(self.apps_dir_path, "apps.json")))
        self.app_configs = json.load(file(os.path.join(self.apps_dir_path, "app_configs.json")))

    def get_app_instances(self):
        return self.configured_app_instances

    def load_app_classes(self):
        """
        The method import and stores class definitions into dict , so they can be used to create app instances .

        """
        for app_def in self.app_defs:
            imp_mod = importlib.import_module("apps.lib." + app_def["name"])
            app_class = getattr(imp_mod, app_def["name"])
            app_class.context = self.context
            self.app_classes = {app_def["name"]:app_class}

    def configure_and_init_app_instance(self):
        """
        Method creates app instances and configures them using configuration definitions .

        """
        for app_config in self.app_configs:
            app_inst = self.app_classes[app_config["name"]](app_config["id"],app_config["alias"],app_config["sub_for"],app_config["pub_to"],app_config["configs"])
            log.info("Apps with id = %s , name = %s , alias = %s was loaded."%(app_inst.id,app_inst.name,app_inst.alias))

            # setting up subscriptions in adapters
            for key,subsc in app_inst.sub_for.iteritems():
                for adapter in self.adapters:
                     adapter.subscribe(subsc)

            self.configured_app_instances.append(app_inst)

    def reload_app(self,app_name):
        # reload("apps.lib." + app_config["name"])
        pass