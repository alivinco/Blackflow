import sys

__author__ = 'alivinco'
import importlib
import json
import os
import logging
log = logging.getLogger("bf_app_manager")

class AppManager:
    def __init__(self, context, adapters):
        self.configured_app_instances = []
        self.app_classes = {}
        self.app_defs = None
        self.app_configs = None
        self.apps_dir_path = "apps"
        self.load_definitions()
        self.context = context
        self.adapters = adapters
        self.load_app_classes()
        # self.configure_and_init_app_instance()
        log.info("App init process completed. %s apps were initialized and configured " % len(self.configured_app_instances))

    def start_apps(self):
        self.configure_and_init_app_instance()

    def load_definitions(self):
        """
        The method loads app and app's configuration definitions from config files

        """
        self.app_defs = json.load(file(os.path.join(self.apps_dir_path, "apps.json")))
        self.app_configs = json.load(file(os.path.join(self.apps_dir_path, "app_configs.json")))

    def get_app_instances(self):
        return self.configured_app_instances

    def get_apps(self):
        return self.app_defs

    def get_app_instance(self, instance_id, instance_alias=None):
        if instance_id:
            return filter(lambda app_inst: app_inst.id == instance_id, self.configured_app_instances)[0]
        elif instance_alias:
            return filter(lambda app_inst: app_inst.alias == instance_alias, self.configured_app_instances)[0]

    def get_app_configs(self):
        return self.app_configs

    def reload_app_instance(self,instance_id,app_name = ""):
        """
        1) unsubscribe from adapters
        2) stop app instance
        3) start new app instance
        :param app_name:
        :param instance_id:
        """
        log.info("Reloading app . id = %s name = %s"%(instance_id,app_name))

        ai = self.get_app_instance(instance_id)
        log.info("Unsubscribing from app's topics")
        for key, topic in ai.sub_for.iteritems():
            for adapter in self.adapters:
                adapter.unsubscribe(topic)
        log.info("Deleting app instance")
        self.configured_app_instances.remove(ai)
        self.load_definitions()
        self.configure_and_init_app_instance(instance_id)

    def reload_app(self, app_name):
        log.info("Reloading app module %s"%app_name)
        mod_ref = sys.modules["apps.lib." + app_name]
        reload(mod_ref)
        mod_ref = sys.modules["apps.lib." + app_name]
        self.app_classes[app_name] = getattr(mod_ref,app_name)
        self.app_classes[app_name].context = self.context
        apps = filter(lambda app_conf:app_conf["name"]==app_name,self.app_configs)
        for app in apps:
            self.reload_app_instance(app["id"],app_name)

    def load_app_classes(self):
        """
        The method import and stores class definitions into dict , so they can be used to create app instances .

        """
        for app_def in self.app_defs:
            imp_mod = importlib.import_module("apps.lib." + app_def["name"])
            app_class = getattr(imp_mod, app_def["name"])
            app_class.context = self.context
            self.app_classes[app_def["name"]] = app_class

    def configure_and_init_app_instance(self, instance_id=None):
        """
        Method creates app instances and configures them using configuration definitions .
        :param instance_id: optional paramters , if not specified then all instances are loaded , if specified then only one instance is loaded
        """
        log.info("Initializing app instance")

        for app_config in self.app_configs:
            if instance_id == None or app_config["id"] == instance_id:
                app_inst = self.app_classes[app_config["name"]](app_config["id"], app_config["alias"], app_config["sub_for"], app_config["pub_to"], app_config["configs"])
                log.info("Apps with id = %s , name = %s , alias = %s was loaded." % (app_inst.id, app_inst.name, app_inst.alias))

                # setting up subscriptions in adapters
                for key, subsc in app_inst.sub_for.iteritems():
                    for adapter in self.adapters:
                        adapter.subscribe(subsc)

                self.configured_app_instances.append(app_inst)
