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
# import logging, logging.config
from libs import logger
# import blackflow.configs.log
from os import environ as env


__author__ = 'alivinco'

is_app_running = True
rule_runner_service = None
mqtt_adapter_service = None
api_mqtt_handler = None


def sigterm_handler(signum, frame):
    global is_app_running
    log.info("Received signal #%d: %s. Shutting down service" % (signum, frame))
    rule_runner_service.stop()
    mqtt_adapter_service.stop()
    api_mqtt_handler.stop()
    logger.stopLogger()
    is_app_running = False


if __name__ == "__main__":

    CONTAINER_NAME = "default"
    LOG_DIR = "./"
    MQTT_CLEAN_SESSION = True
    MQTT_HOST = "localhost"
    MQTT_PORT = 1883
    MQTT_USERNAME = None
    MQTT_PASSWORD = None
    MQTT_CLIENTID = ""
    GLOBAL_PREFIX = ""

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='Config file path', default=None)
    parser.add_argument('-a', '--apps', help='Apps storage folder', required=True)
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
            MQTT_USERNAME = configs["mqtt"]["username"]
            MQTT_PASSWORD = configs["mqtt"]["password"]
    else:
        configs = {"instance_config": {"name": "default"}}

    if args.mqtt_host: MQTT_HOST = args.mqtt_host
    if args.mqtt_port: MQTT_PORT = int(args.mqtt_port)
    if args.mqtt_user: MQTT_USERNAME = args.mqtt_user
    if args.mqtt_pass: MQTT_PASSWORD = args.mqtt_pass
    if args.log_dir: LOG_DIR = args.log_dir
    if args.name: CONTAINER_NAME = args.name

    if env.get("ZM_MQTT_BROKER_ADDR"):
        add_split = env.get("ZM_MQTT_BROKER_ADDR").split(":")
        MQTT_HOST = add_split[0]
        if len(add_split) == 2:
            MQTT_PORT = add_split[1]
    if env.get("ZM_MQTT_USERNAME"):
        MQTT_USERNAME = env.get("ZM_MQTT_USERNAME")
    if env.get("ZM_MQTT_PASSWORD"):
        MQTT_PASSWORD = env.get("ZM_MQTT_PASSWORD")
    if env.get("ZM_MQTT_CLIENTID"):
        MQTT_CLIENTID = env.get("ZM_MQTT_CLIENTID")
    else:
        MQTT_CLIENTID = "blackflow_" + CONTAINER_NAME
    if env.get("ZM_MQTT_CLEAN_SESSION"):
        MQTT_CLEAN_SESSION = env.get("ZM_MQTT_CLEAN_SESSION")

    if env.get("ZM_APP_INSTANCE"):
        CONTAINER_NAME = env.get("ZM_APP_INSTANCE")
    if env.get("ZM_DOMAIN"):
        GLOBAL_PREFIX = env.get("ZM_DOMAIN")
    elif configs["mqtt"]["topic_prefix"]:
        GLOBAL_PREFIX = configs["mqtt"]["topic_prefix"]

    configs["instance_config"]["name"] = CONTAINER_NAME

    print "Starting service with parameters :"
    print "CONTAINER_NAME=%s" % CONTAINER_NAME
    print "GLOBAL_PREFIX=%s" % GLOBAL_PREFIX
    print "MQTT_CLEAN_SESSION=%s" % MQTT_CLEAN_SESSION
    print "MQTT_CLIENTID=%s" % MQTT_CLIENTID
    print "MQTT_HOST=%s" % MQTT_HOST
    print "MQTT_PORT=%s" % MQTT_PORT
    print "APPS_DIR=%s" % args.apps
    print "LOG_DIR=%s" % LOG_DIR

    # blackflow.configs.log.config["handlers"]["info_file_handler"]["filename"] = os.path.join(LOG_DIR, "blackflow_info.log")
    # blackflow.configs.log.config["handlers"]["error_file_handler"]["filename"] = os.path.join(LOG_DIR, "blackflow_error.log")
    # logging.config.dictConfig(blackflow.configs.log.config)
    configs["apps_dir_path"] = args.apps

    log = logger.getLogger("bf_service")
    logger.configure("blackflow.log")

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)
    adapters = []
    log.info("Starting application.Blackflow instance name = %s" % CONTAINER_NAME)
    storage_file = os.path.join(args.apps, "data", CONTAINER_NAME + ".db")
    context = BfContext(storage_path=storage_file)

    mqtt_adapter_service = MqttAdapter(context, CONTAINER_NAME, client_id=MQTT_CLIENTID, host=MQTT_HOST, port=MQTT_PORT, username=MQTT_USERNAME, password=MQTT_PASSWORD , use_clean_session=MQTT_CLEAN_SESSION)
    if GLOBAL_PREFIX:
        mqtt_adapter_service.set_global_prefix(GLOBAL_PREFIX)

    adapters.append(mqtt_adapter_service)
    sys.path.append(args.apps.replace("apps", ""))
    app_manager = AppManager(context, adapters, args.apps, configs=configs)

    rule_runner_service = AppRunner(context, adapters, app_manager)
    api_mqtt_handler = ApiMqttHandler(app_manager, mqtt_adapter_service, context, CONTAINER_NAME, configs)
    mqtt_adapter_service.set_api_handler(api_mqtt_handler)

    rule_runner_service.start()
    mqtt_adapter_service.start()
    api_mqtt_handler.start()
    app_manager.start_apps()

    while is_app_running:
        time.sleep(1)
