import sys
from threading import Lock
from blackflow.libs.utils import get_next_id
from blackflow.core.app_scheduler import AppScheduler
from blackflow.libs.utils import split_app_full_name, compose_app_full_name
from libs import logger
import importlib
import json
import os
import shutil

__author__ = 'alivinco'
log = logger.getLogger("app_manager")


class AppInstanceState:
    STOPPED = 0
    LOADED = 1
    INITIALIZED = 2
    RUNNING = 3
    PAUSED = 4
    STOPPED_WITH_ERROR = 5
    PAUSED_WITH_ERROR = 6


class AppManager:
    # application states

    def __init__(self, context, adapters, apps_dir_path, configs ={}):
        self.apps_dir_path = apps_dir_path
        self.app_instances = []
        self.app_classes = {}
        self.app_manifests = []
        # self.app_defs_path = os.path.join(self.apps_dir_path, "apps.json")
        self.app_instances_configs = []
        self.context = context
        self.adapters = adapters
        self.instances_config_file = os.path.join(self.apps_dir_path,"data",configs["instance_config"]["name"]+"_app_configs.json")
        self.instances_config_lock = Lock()
        self.scheduler = AppScheduler()
        self.scheduler.init_scheduler()
        self.configs = configs
        # self.configure_and_init_app_instance()
        log.info("App init process completed. %s apps were initialized and configured " % len(self.app_instances))

    def start_apps(self):
        self.load_app_manifests()
        self.load_app_instances_configs()
        self.load_all_app_classes()
        self.configure_and_init_app_instance(is_system_startup=True)

    def init_new_app(self, developer, name, version=""):
        """
        The method initializes new app by creating app folder , app file and descriptor
        :param name:
        :param version:
        :param developer
        """
        version = str(version)
        app_full_name = compose_app_full_name(developer, name, version)
        new_app_dir = os.path.join(self.apps_dir_path, "lib", app_full_name)
        if not os.path.exists(new_app_dir):
            # 1. creating application folder
            os.makedirs(new_app_dir)
            open(os.path.join(new_app_dir, "__init__.py"), "w").close()
            # 2. reading application template
            with open(os.path.join("blackflow", "libs", "app_template.py"), "r") as f:
                app_template = f.read()
                app_template = app_template.replace("BfApplicationTemplate", name)
            # 3. writing application template
            with open(os.path.join(new_app_dir, "%s.py" % name), "w") as f:
                f.write(app_template)
            # 4. writing application descriptor
            descr_template = {"name": name, "version": version,"developer": developer, "description": "", "sub_for": {}, "pub_to": {}, "configs": {}}
            with open(os.path.join(new_app_dir, "manifest.json"), "w") as f:
                f.write(json.dumps(descr_template))
            self.app_manifests.append(descr_template)
            log.info("Manifest for %s app was loaded" % (app_full_name))
            return (True, "")
        else:
            warn_msg = "App with name %s and version %s already exists , specify another name or version" % (name, version)
            log.warn(warn_msg)
            return (False, warn_msg)

    def delete_app(self, app_full_name):
        """
        Deletes application and all it's instance from system completely.
        :param app_full_name:
        """
        ai = self.get_app_instances_configs(app_full_name=app_full_name)
        log.info("Deleting app %s" % app_full_name)
        for ai_item in ai:
            log.info("Deleting app instance %s" % ai_item["alias"])
            self.delete_app_instance(ai_item["id"])
        log.info("Deleting application manifest")
        ad = self.get_app_manifest(app_full_name)
        self.app_manifests.remove(ad)
        app_dir = os.path.join(self.apps_dir_path, "lib", app_full_name)
        log.info("Deleting app folder %s" % app_dir)
        shutil.rmtree(app_dir)
        log.info("App %s was deleted" % app_full_name)

    def delete_app_instance(self, instance_id):
        """
        Deletes application instance object , unsubscribese from all topics and removes entry from app_config.json
        :param instance_id:
        """
        self.stop_app_instance(instance_id)
        aic = self.get_app_instances_configs(instance_id=instance_id)
        # invoking on_uninstall callback , so app can run cleanup routines .
        ai_obj = self.get_app_instance_obj(instance_id)
        try:
            if hasattr(ai_obj,"on_uninstall"):
                ai_obj.on_uninstall()
        except Exception as ex:
            log.exception(ex)
        if aic:
            self.app_instances_configs.remove(aic[0])
            self.serialize_instances_config()

    def serialize_instances_config(self):
        log.info("Serializing instances config to file " + self.instances_config_file)
        f = open(self.instances_config_file, "w")
        f.write(json.dumps(self.app_instances_configs, indent=True))
        f.close()

    def load_app_instances_configs(self):
        """
        Loads all app instance configurations

        """
        try:
            self.app_instances_configs = json.load(file(self.instances_config_file))
            for item in self.app_instances_configs:
                item["state"] = AppInstanceState.STOPPED
        except IOError:
            # app folder is empty and needs to be initialized
            f = open(self.instances_config_file, "w")
            f.write("[]")
            f.close()
            self.app_instances_configs = []

    def load_app_manifests(self):
        """
        Loads all application manifests from lib folders

        """
        self.app_manifests = []
        apps_lib_path = os.path.join(self.apps_dir_path, "lib")
        for app_dir in os.listdir(apps_lib_path):
            if app_dir not in ("__init__.py", "__init__.pyc"):
                if app_dir.find("_v") > 1:
                    app_name = app_dir[:app_dir.find("_v")]
                    self.app_manifests.append(json.load(file(os.path.join(self.apps_dir_path, 'lib', app_dir, "manifest.json"))))
                    log.info("Manifest for %s app was loaded" % (app_dir))
                else:
                    log.info("Directory %s will be skipped from app loader . Doesn't match naming convention ." % app_dir)

    def configure_app_instance(self, id, app_full_name, alias, sub_for, pub_to, configs, comments, auto_startup="START", schedules=[]):
        """
        Appends new or modifies existing app instance configuration . The methods modifies data structure ,
        serializes it to disk but doesn't reload actual instance .
        :param schedules:
        :param id: Application instance id
        :type id: int
        :param app_full_name: Application full name = developer + App name + version
        :type app_full_name: string
        :param alias: Instance Alias
        :type alias: string
        :param sub_for: Dictionary of topics application is subscribing for
        :param pub_to:
        :param configs:
        :param comments:
        :param auto_startup:
        :return:
        """
        with self.instances_config_lock:
            inst_conf_list = filter(lambda conf: conf["id"] == id, self.app_instances_configs)
            if len(inst_conf_list) == 0:
                inst_id = get_next_id(self.app_instances_configs)
                inst_conf = {"id": inst_id}
                inst_conf["app_full_name"] = app_full_name
                self.app_instances_configs.append(inst_conf)
            else:
                inst_conf = inst_conf_list[0]
                inst_id = id

            inst_conf["alias"] = alias
            inst_conf["sub_for"] = sub_for
            inst_conf["pub_to"] = pub_to
            inst_conf["configs"] = configs
            inst_conf["comments"] = comments
            # TODO: Check existing state first
            inst_conf["state"] = AppInstanceState.STOPPED
            inst_conf["auto_startup"] = auto_startup
            inst_conf["schedules"] = schedules

            self.serialize_instances_config()
        return inst_id

    def get_app_instances(self):
        return self.app_instances

    def get_app_instance_obj(self, instance_id, instance_alias=None):
        """
        Returns application instance object
        :param instance_id:
        :param instance_alias:
        :return:
        """
        try:
            if instance_id:
                return filter(lambda app_inst: app_inst.id == instance_id, self.app_instances)[0]
            elif instance_alias:
                return filter(lambda app_inst: app_inst.alias == instance_alias, self.app_instances)[0]
        except:
            return None

    def get_app_instances_configs(self, instance_id=None, instance_alias=None, app_full_name=None):
        """
        Returns application instance configuration object
        :param instance_id:
        :param instance_alias:
        :param app_full_name:
        :return list of instance configurations:
        """
        try:
            if instance_id:
                return filter(lambda app_inst: app_inst["id"] == instance_id, self.app_instances_configs)
            elif instance_alias:
                return filter(lambda app_inst: app_inst["alias"] == instance_alias, self.app_instances_configs)
            elif app_full_name:
                return filter(lambda app_inst: app_inst["app_full_name"] == app_full_name, self.app_instances_configs)
        except Exception as ex:
            log.error("Instance can't be found because of error %s" % ex)
            return None

    def get_app_manifests(self,sfilter = None):
        """
        Return list of all app manifests .

        :param sfilter: search filter , so far supported fields : name , version , developer
        :return:
        """
        if sfilter:
            try:
                return filter(lambda app: app["developer"] == sfilter["developer"] and
                                           app["name"] == sfilter["name"] and
                                           app["version"] == sfilter["version"], self.app_manifests)
            except:
                return []
        else :
            return self.app_manifests

    def load_app_manifest(self,app_full_name):
        self.app_manifests.append(json.load(file(os.path.join(self.apps_dir_path, 'lib', app_full_name, "manifest.json"))))

    def get_app_manifest(self, app_full_name):
        developer,app_name, version = split_app_full_name(app_full_name)
        try:
            return filter(lambda app_manif:app_manif["developer"] == developer and app_manif["name"] == app_name and app_manif["version"] == version, self.app_manifests)
        except:
            return None

    def get_app_configs(self,sfilter = None):
        """
        Return list of application instances
        :param sfilter: response can be filtered by id by setting sfilter["id"]
        :return:
        """
        if sfilter:
            try:
                return filter(lambda app: app["id"] == sfilter["id"],self.app_instances_configs)
            except:
                return []
        else:
            return self.app_instances_configs

    def stop_app_instance(self, instance_id):
        ai = self.get_app_instance_obj(instance_id)
        if ai:
            log.info("Unsubscribing from app's topics")
            for key, topic in ai.sub_for.iteritems():
                for adapter in self.adapters:
                    adapter.unsubscribe(topic["topic"])
            self.scheduler.remove_schedules_for_instance(instance_id)
            log.info("Invoking on_stop callback")
            try:
                if hasattr(ai,"on_stop"):
                    ai.on_stop()
            except Exception as ex:
                log.exception(ex)
            log.info("Deleting app instance oobject")
            self.app_instances.remove(ai)
            self.get_app_instances_configs(instance_id=instance_id)[0]["state"] = AppInstanceState.STOPPED
            return True
        else:
            return False

    def pause_app_instance(self, instance_id):
        ai = self.get_app_instance_obj(instance_id)
        if ai:
            log.info("Pausing application instance , instance id = %s" % instance_id)
            for key, topic in ai.sub_for.iteritems():
                for adapter in self.adapters:
                    adapter.unsubscribe(topic["topic"])
            self.get_app_instances_configs(instance_id=instance_id)[0]["state"] = AppInstanceState.PAUSED
            return True
        else:
            return False

    def start_app_instance(self, instance_id):
        app_config = self.get_app_instances_configs(instance_id=instance_id)[0]
        state = app_config["state"]
        if state == AppInstanceState.STOPPED or state == AppInstanceState.STOPPED_WITH_ERROR:
            log.info("Starting stopped application instance ,instance id = %s" % instance_id)
            self.configure_and_init_app_instance(instance_id=instance_id)
            return True
        elif state == AppInstanceState.PAUSED or state == AppInstanceState.PAUSED_WITH_ERROR:
            app_inst = self.get_app_instance_obj(instance_id=instance_id)
            try:
                app_inst.on_start()
                log.info("Resuming paused application instance ,instance id = %s" % instance_id)
                for key, subsc in app_inst.sub_for.iteritems():
                    for adapter in self.adapters:
                        adapter.subscribe(subsc["topic"])
                if len(app_config["schedules"]) > 0:
                        self.scheduler.init_schedule(app_config,app_inst)
                app_config["state"] = AppInstanceState.RUNNING
                return True
            except Exception as ex:
                app_config["error"] = str(ex)
                app_config["state"] = AppInstanceState.PAUSED_WITH_ERROR
                return False
        else:
            log.info("Application instance can't be started since it is already in state %s" % state)
            return False

    def reload_app_instance(self, instance_id, app_name=""):
        """
        The method recreates app instance . Class is not reloaded .
        Should be invoked after configuration parameters were modified .
        1) unsubscribe from adapters
        2) stop app instance
        3) start new app instance
        :param app_name:
        :param instance_id:
        """
        log.info("Reloading app . id = %s name = %s" % (instance_id, app_name))
        if self.stop_app_instance(instance_id):
            self.load_app_instances_configs()
        self.configure_and_init_app_instance(instance_id)

    def reload_app(self, app_full_name):
        """
        Reloads app class and reinitialize app instance . Should be invoked when app source code was changed.
        :param app_full_name:
        """
        log.info("Reloading app module %s" % app_full_name)
        developer, app_name, version = split_app_full_name(app_full_name)
        mod_ref = sys.modules["apps.lib.%s.%s" % (app_full_name, app_name)]
        reload_success = False
        try:
            reload(mod_ref)
            reload_success = True
        except Exception as ex:
            log.exception(ex)
            error = str(ex)
            # TODO: Send notification via API

        if reload_success:
            mod_ref = sys.modules["apps.lib.%s.%s" % (app_full_name, app_name)]
            self.app_classes[app_full_name] = getattr(mod_ref, app_name)
            self.app_classes[app_full_name].context = self.context
            apps = filter(lambda app_conf: app_conf["app_full_name"] == app_full_name, self.app_instances_configs)
            for app in apps:
                self.reload_app_instance(app["id"], app_full_name)
            return True, None
        else:
            return False, error

    def load_all_app_classes(self):
        """
        Loads all application classes into dictionary , so they can be used to create app instances .

        """
        for app_manif in self.app_manifests:
                app_full_name = compose_app_full_name(app_manif["developer"],app_manif["name"], app_manif["version"])
                log.debug("App %s class was loaded "%app_full_name)
                self.load_app_class(app_full_name)

    def load_app_class(self, app_full_name):
        """
        Loads application manifest and class .
        :param app_name: App name
        :param instance_id: App configuration instance id
        """
        log.info("Loading %s app descriptor and class" % app_full_name)
        try:
            # loading application class
            developer,app_name, version = split_app_full_name(app_full_name)
            imp_mod = importlib.import_module("apps.lib.%s.%s" % (app_full_name, app_name))
            app_class = getattr(imp_mod, app_name)
            app_class.context = self.context
            self.app_classes[app_full_name] = app_class

            for ai in self.get_app_instances_configs(app_full_name=app_full_name):
                ai["state"] = AppInstanceState.LOADED
                log.debug("App instance %s state was changed to LOADED" % ai["alias"])
        except ImportError as ex:
                log.error("App %s can't be loaded because of classloader error %s " % (app_full_name, ex))
        except Exception as ex:
            log.exception(ex)
            # TODO: post error via msg adapter

    def set_instance_state(self, instance_id, state):
        pass

    def configure_and_init_app_instance(self, instance_id=None, is_system_startup=False):
        """
        Method creates application instances objects and configures them using configuration definitions .
        :param instance_id: optional paramters , if not specified then all instances are loaded , if specified then only one instance is loaded
        """
        log.info("Initializing app instance . Instance id = %s" % instance_id)

        for app_config in self.app_instances_configs:
            if (instance_id is None or app_config["id"] == instance_id) and (
                        (is_system_startup == True and app_config["auto_startup"] == "START") or is_system_startup == False):

                app_full_name = app_config["app_full_name"]
                if not(app_full_name in self.app_classes):
                    self.load_app_class(app_full_name)

                try:
                    app_inst = self.app_classes[app_full_name](app_config["id"], app_config["alias"], app_config["sub_for"], app_config["pub_to"],app_config["configs"])
                    app_inst.on_start()
                    # Add job to scheduler here
                    app_config["state"] = AppInstanceState.INITIALIZED
                    log.debug("App instance %s state was changed to INITIALIZED" % app_config["alias"])
                    # setting up subscriptions in adapters
                    for key, subsc in app_inst.sub_for.iteritems():
                        for adapter in self.adapters:
                            adapter.subscribe(subsc["topic"])
                    app_config["state"] = AppInstanceState.RUNNING
                    if len(app_config["schedules"]) > 0:
                        self.scheduler.init_schedule(app_config,app_inst)
                    self.app_instances.append(app_inst)
                except Exception as ex:
                    log.error("App %s can't be started because of error ")
                    log.exception(ex)
                    app_config["state"] = AppInstanceState.STOPPED_WITH_ERROR
                    log.debug("App instance %s state was changed to STOPPED_WITH_ERROR" % app_config["alias"])
                    app_config["error"] = str(ex)

                log.info("Apps with id = %s , name = %s , alias = %s was loaded." % (app_inst.id, app_inst.name, app_inst.alias))
