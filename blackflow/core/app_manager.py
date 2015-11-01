import sys
from threading import Lock
from blackflow.libs.utils import get_next_id

__author__ = 'alivinco'
import importlib
import json
import os
import logging
import shutil
log = logging.getLogger("bf_app_manager")

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

    def __init__(self, context, adapters,apps_dir_path):
        self.apps_dir_path = apps_dir_path
        self.app_instances = []
        self.app_classes = {}
        self.app_descriptors = []
        # self.app_defs_path = os.path.join(self.apps_dir_path, "apps.json")
        self.app_instances_configs = []
        self.context = context
        self.adapters = adapters
        self.instances_config_file = os.path.join(self.apps_dir_path, "app_configs.json")
        self.instances_config_lock = Lock()
        # self.configure_and_init_app_instance()
        log.info("App init process completed. %s apps were initialized and configured " % len(self.app_instances))

    def start_apps(self):
        self.load_app_descriptors()
        self.load_app_instances_configs()
        self.load_app_classes()
        self.configure_and_init_app_instance(is_system_startup=True)

    def init_new_app(self,name,version=""):
        """
        The method initializes new app by creating app folder , app file and descriptor
        :param name:
        :param version:
        """
        app_full_name = "%s_%s"%(name,version)
        new_app_dir = os.path.join(self.apps_dir_path,"lib",app_full_name)
        if not os.path.exists(new_app_dir):
            # 1. creating application folder
            os.makedirs(new_app_dir)
            open(os.path.join(new_app_dir,"__init__.py"),"w").close()
            # 2. reading application template
            with open(os.path.join("blackflow","libs","app_template.py"),"r") as f:
                app_template = f.read()
                app_template = app_template.replace("BfApplicationTemplate",app_full_name)
            # 3. writing application template
            with open(os.path.join(new_app_dir,"%s.py"%app_full_name),"w") as f:
                f.write(app_template)
            # 4. writing application descriptor
            descr_template = {"name":name,"version":version,"description":"","sub_for":{},"pub_to":{},"configs":{}}
            with open(os.path.join(new_app_dir,"%s.json"%app_full_name),"w") as f:
                f.write(json.dumps(descr_template))
            self.app_descriptors.append(descr_template)
            log.info("Descriptor for %s app was loaded"%(app_full_name))
            return (True,"")
        else :
            warn_msg = "App with name %s and version %s already exists , specify another name or version"%(name,version)
            log.warn(warn_msg)
            return (False,warn_msg)

    def add_new_app(self,name,sub_for,pub_to,configs,src):
        f_name = os.path.join(self.app_instances_configs,"lib",name)
        with open(f_name,"w") as f :
            f.write(src)
        self.serialize_app_defs()

    def delete_app(self,app_name):
        """
        Deletes app from system completely.
        :param app_name:
        """
        ai = self.get_app_instances_configs(app_name=app_name)
        log.info("Deleting app %s"%app_name)
        for ai_item in ai:
            log.info("Deleting app instance %s"%ai_item.alias)
            self.delete_app_instance(ai_item.get_id())
            log.info("Deleting app descriptor")
            ad = self.get_app_descriptor(app_name)
            self.app_descriptors.remove(ad)
            app_dir = os.path.join(self.apps_dir_path,"lib",ai_item.name)
            log.info("Deleting app folder %s"%app_dir)
            shutil.rmtree()
        log.info("App %s was deleted"%app_name)

    def delete_app_instance(self,instance_id):
        """
        Deletes application instance object , unsubscribese from all topics and removes entry from app_config.json
        :param instance_id:
        """
        self.stop_app_instance(instance_id)
        aic = self.get_app_instances_configs(instance_id=instance_id)
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
            f = open(self.instances_config_file,"w")
            f.write("[]")
            f.close()
            self.app_instances_configs = []

    def load_app_descriptors(self):
        """
        Loads all application descriptors from lib folders

        """
        self.app_descriptors = []
        apps_lib_path = os.path.join(self.apps_dir_path,"lib")
        for item in os.listdir(apps_lib_path):
            if item not in ("__init__.py","__init__.pyc"):
                self.app_descriptors.append(json.load(file(os.path.join(self.apps_dir_path,'lib',item, item+".json"))))
                log.info("Descriptor for %s app was loaded"%(item))

    def configure_app_instance(self,id,app_name,alias,sub_for,pub_to,configs,comments,auto_startup="RUN"):
        with self.instances_config_lock:
            inst_conf_list = filter(lambda conf : conf["id"]==id,self.app_instances_configs)
            if len(inst_conf_list)==0:
                inst_id = get_next_id(self.app_instances_configs)
                inst_conf = {"id": inst_id}
                inst_conf["name"] = app_name
                self.app_instances_configs.append(inst_conf)
            else:
                inst_conf = inst_conf_list[0]
                inst_id = id

            inst_conf["alias"] = alias
            inst_conf["sub_for"] = sub_for
            inst_conf["pub_to"] = pub_to
            inst_conf["configs"] = configs
            inst_conf["comments"] = comments
            inst_conf["state"] = AppInstanceState.STOPPED
            inst_conf["auto_startup"] = auto_startup

            self.serialize_instances_config()
        return inst_id

    def get_app_instances(self):
        return self.app_instances

    def get_apps(self):
        """
        Return list of app descriptors .

        :return:
        """
        return self.app_descriptors

    def get_app_instance_obj(self, instance_id, instance_alias=None):
        """
        Returns instance object
        :param instance_id:
        :param instance_alias:
        :return:
        """
        try :
            if instance_id:
                return filter(lambda app_inst: app_inst.id == instance_id, self.app_instances)[0]
            elif instance_alias:
                return filter(lambda app_inst: app_inst.alias == instance_alias, self.app_instances)[0]
        except :
            return None

    def get_app_instances_configs(self, instance_id=None, instance_alias=None,app_name=None):
        """
        Returns application instance configuration object
        :param instance_id:
        :param instance_alias:
        :param app_name:
        :return list of instance configurations:
        """
        try:
            if instance_id:
                return filter(lambda app_inst: app_inst["id"] == instance_id, self.app_instances_configs)
            elif instance_alias:
                return filter(lambda app_inst: app_inst["alias"] == instance_alias, self.app_instances_configs)
            elif app_name:
                return filter(lambda app_inst: app_inst["name"] == app_name, self.app_instances_configs)
        except Exception as ex:
            log.error("Instance can't be found because of error %s"%ex)
            return None

    def get_app_descriptor(self,app_name):
        try:
            return filter(lambda app_disc: app_disc["name"] == app_name, self.app_descriptors)[0]
        except:
            return None

    def get_app_configs(self):
        return self.app_instances_configs

    def stop_app_instance(self,instance_id):
        ai = self.get_app_instance_obj(instance_id)
        if ai :
            log.info("Unsubscribing from app's topics")
            for key, topic in ai.sub_for.iteritems():
                for adapter in self.adapters:
                    adapter.unsubscribe(topic["topic"])
            log.info("Deleting app instance oobject")
            self.app_instances.remove(ai)
            self.get_app_instances_configs(instance_id=instance_id)[0]["state"] = AppInstanceState.STOPPED
            return True
        else :
            return False

    def pause_app_instance(self,instance_id):
        ai = self.get_app_instance_obj(instance_id)
        if ai :
            log.info("Pausing application instance , instance id = %s"%instance_id)
            for key, topic in ai.sub_for.iteritems():
                for adapter in self.adapters:
                    adapter.unsubscribe(topic["topic"])
            self.get_app_instances_configs(instance_id=instance_id)[0]["state"] = AppInstanceState.PAUSED
            return True
        else :
            return False

    def start_app_instance(self,instance_id):
        app_config = self.get_app_instances_configs(instance_id=instance_id)[0]
        state = app_config["state"]
        if state == AppInstanceState.STOPPED or state == AppInstanceState.STOPPED_WITH_ERROR :
            log.info("Starting stopped application instance ,instance id = %s"%instance_id)
            self.configure_and_init_app_instance(instance_id=instance_id)
            return True
        elif state == AppInstanceState.PAUSED or state == AppInstanceState.PAUSED_WITH_ERROR :
            app_inst = self.get_app_instance_obj(instance_id=instance_id)
            try:
                app_inst.on_start()
                log.info("Reesuming paused application instance ,instance id = %s"%instance_id)
                for key, subsc in app_inst.sub_for.iteritems():
                        for adapter in self.adapters:
                            adapter.subscribe(subsc["topic"])
                app_config["state"] = AppInstanceState.RUNNING
                return True
            except Exception as ex :
                app_config["error"] = str(ex)
                app_config["state"] = AppInstanceState.PAUSED_WITH_ERROR
                return False
        else:
            log.info("Application instance can't be started since it is already in state %s"%state)
            return False

    def reload_app_instance(self,instance_id,app_name = ""):
        """
        The method recreates app instance . Class is not reloaded .
        Should be invoked after configuration parameters were modified .
        1) unsubscribe from adapters
        2) stop app instance
        3) start new app instance
        :param app_name:
        :param instance_id:
        """
        log.info("Reloading app . id = %s name = %s"%(instance_id,app_name))
        if self.stop_app_instance(instance_id):
            self.load_app_instances_configs()
        self.configure_and_init_app_instance(instance_id)

    def load_new_app(self , app_name):
        """
        The method loads and initializes new app
        :param app_name: App name
        :param instance_id: App configuration instance id
        """
        log.info("Loading %s app descriptor and class"%app_name)
        try:
            self.app_descriptors.append(json.load(file(os.path.join(self.apps_dir_path,'lib',app_name, app_name+".json"))))
            # loading app class
            imp_mod = importlib.import_module("apps.lib.%s.%s"%(app_name,app_name))
            app_class = getattr(imp_mod, app_name)
            app_class.context = self.context
            self.app_classes[app_name] = app_class

            for ai in self.get_app_instances_configs(app_name=app_name):
                ai["state"] = AppInstanceState.LOADED
                log.debug("App instance %s state was changed to LOADED"%ai["alias"])

        except Exception as ex:
            log.exception(ex)
            #TODO: post error via msg adapter

    def reload_app(self, app_name):
        """
        Reloads app class and reinitialize app instance . Should be invoked when app source code was changed.
        :param app_name:
        """
        log.info("Reloading app module %s"%app_name)
        mod_ref = sys.modules["apps.lib.%s.%s"%(app_name,app_name)]
        reload_success = False
        try:
            reload(mod_ref)
            reload_success = True
        except Exception as ex:
            log.exception(ex)
            error = str(ex)
            #TODO: Send notification via API

        if reload_success:
            mod_ref = sys.modules["apps.lib.%s.%s"%(app_name,app_name)]
            self.app_classes[app_name] = getattr(mod_ref,app_name)
            self.app_classes[app_name].context = self.context
            apps = filter(lambda app_conf:app_conf["name"]==app_name,self.app_instances_configs)
            for app in apps:
                self.reload_app_instance(app["id"],app_name)
            return True, None
        else :
            return False, error

    def load_app_classes(self):
        """
        The method import and stores class definitions into dict , so they can be used to create app instances .

        """
        for app_def in self.app_descriptors:
            try:
                imp_mod = importlib.import_module("apps.lib.%s.%s"%(app_def["name"],app_def["name"]))
                app_class = getattr(imp_mod, app_def["name"])
                app_class.context = self.context
                self.app_classes[app_def["name"]] = app_class
            except ImportError as ex :
                log.error("App %s can't be loaded because of classloader error %s "%(app_def["name"],ex))

    def set_instance_state(self,instance_id,state):
        pass

    def configure_and_init_app_instance(self, instance_id=None, is_system_startup=False):
        """
        Method creates application instances objects and configures them using configuration definitions .
        :param instance_id: optional paramters , if not specified then all instances are loaded , if specified then only one instance is loaded
        """
        log.info("Initializing app instance . Instance id = %s"%instance_id)

        for app_config in self.app_instances_configs:
            if (instance_id is None or app_config["id"] == instance_id) and ((is_system_startup==True and app_config["auto_startup"]=="START") or is_system_startup==False) :
                app_inst = self.app_classes[app_config["name"]](app_config["id"], app_config["alias"], app_config["sub_for"], app_config["pub_to"], app_config["configs"])
                try:
                    app_inst.on_start()
                    app_config["state"] = AppInstanceState.INITIALIZED
                    log.debug("App instance %s state was changed to INITIALIZED"%app_config["alias"])
                     # setting up subscriptions in adapters
                    for key, subsc in app_inst.sub_for.iteritems():
                        for adapter in self.adapters:
                            adapter.subscribe(subsc["topic"])
                    app_config["state"] = AppInstanceState.RUNNING
                    self.app_instances.append(app_inst)
                except Exception as ex:
                    log.error("App %s can be started of error ")
                    log.exception(ex)
                    app_config["state"] = AppInstanceState.STOPPED_WITH_ERROR
                    log.debug("App instance %s state was changed to STOPPED_WITH_ERROR"%app_config["alias"])
                    app_config["error"] = str(ex)

                log.info("Apps with id = %s , name = %s , alias = %s was loaded." % (app_inst.id, app_inst.name, app_inst.alias))


