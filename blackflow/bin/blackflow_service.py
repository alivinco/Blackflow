import json
import os
import sys
sys.path.append("./blackflow/libs/site-packages")
import signal
import time
import argparse
from blackflow.libs.context import BfContext
from blackflow.adapters.mqtt_adapter import MqttAdapter
from blackflow.core.app_manager import AppManager
from blackflow.core.app_runner import AppRunner
from blackflow.handlers.api_mqtt_handler import ApiMqttHandler
from smartlylib.service.Service import ServiceManager, ServiceState
import logging, logging.config
import blackflow.configs.log
import requests
__author__ = 'alivinco'


def sigterm_handler(signum, frame):
        log.info("Received signal #%d: %s. Shutting down service" % (signum, frame))
        service_manager.stop()

if __name__ == "__main__":

    CONTAINER_NAME = "default"
    LOG_DIR = "./"
    MQTT_HOST = "localhost"
    MQTT_PORT = 1883
    MQTT_USERNAME = None
    MQTT_PASSWORD = None

    # print requests.get('https://github.com')
    # print requests.get('https://zmarlin.com')

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='Config file path', default=None)
    parser.add_argument('-a', '--apps', help='Apps storage folder',required=True)
    parser.add_argument('-n', '--name', help='Instance name', default=None)
    parser.add_argument('-l', '--log_dir', help='Directory for logs', default=None)
    parser.add_argument('-mqh', '--mqtt_host', help='Mqtt broker host name', default=None)
    parser.add_argument('-mqp', '--mqtt_port', help='Mqtt broker port', default=None)
    parser.add_argument('-mu', '--mqtt_user', help='Mqtt broker username', default=None)
    parser.add_argument('-mp', '--mqtt_pass', help='Mqtt broker password', default=None)
    args = parser.parse_args()

    if args.conf:
        with open(args.conf, "r") as app_file:
            configs = json.loads(app_file.read())
            CONTAINER_NAME = configs["instance_config"]["name"]
            LOG_DIR = configs["log_dir"]
            MQTT_HOST = configs["mqtt"]["host"]
            MQTT_PORT = configs["mqtt"]["port"]
    else :
        configs = {"instance_config":{"name":"default"}}

    if args.mqtt_host: MQTT_HOST = args.mqtt_host
    if args.mqtt_port: MQTT_PORT = int(args.mqtt_port)
    if args.log_dir: LOG_DIR = args.log_dir
    if args.name: CONTAINER_NAME = args.name

    configs["instance_config"]["name"] = CONTAINER_NAME

    print "Starting service with parameters :"
    print "CONTAINER_NAME=%s"%CONTAINER_NAME
    print "LOG_DIR=%s"%LOG_DIR
    print "MQTT_HOST=%s"%MQTT_HOST
    print "MQTT_PORT=%s"%MQTT_PORT
    print "APPS_DIR=%s"%args.apps

    blackflow.configs.log.config["handlers"]["info_file_handler"]["filename"] = os.path.join(LOG_DIR,"blackflow_info.log")
    blackflow.configs.log.config["handlers"]["error_file_handler"]["filename"] = os.path.join(LOG_DIR,"blackflow_error.log")
    logging.config.dictConfig(blackflow.configs.log.config)
    configs["apps_dir_path"] = args.apps

    log = logging.getLogger("bf_service")

    service_manager = ServiceManager("main")
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)
    adapters = []
    log.info("Starting application.Blackflow instance name = %s"%CONTAINER_NAME)
    storage_file = os.path.join(args.apps,"data",CONTAINER_NAME+".db")
    context = BfContext(storage_path=storage_file)

    mqtt_adapter_service = MqttAdapter(context,CONTAINER_NAME,client_id="blackflow_"+CONTAINER_NAME,host=MQTT_HOST,port=MQTT_PORT)
    adapters.append(mqtt_adapter_service)
    sys.path.append(args.apps.replace("apps",""))
    app_manager = AppManager(context,adapters,args.apps,configs=configs)
    rule_runner_service = AppRunner(context,adapters,app_manager)
    api_mqtt_handler = ApiMqttHandler(app_manager,mqtt_adapter_service,context,CONTAINER_NAME,configs)
    mqtt_adapter_service.set_api_handler(api_mqtt_handler)

    service_manager.register(rule_runner_service)
    service_manager.register(mqtt_adapter_service)

    # service = ServiceRunner(RuleRunner(context))
    service_manager.start()
    service_manager.waitStartup(10)
    # app manager and api ghandler can be initialized only when mqtt adapter is running.
    app_manager.start_apps()
    api_mqtt_handler.start()

    while service_manager.getState() == ServiceState.RUN:
        time.sleep(1)
    if not service_manager.waitShutdown(10):
        log.error("Service Manager was not able to shut down all services in time. Unclean Shutdown !!!")
