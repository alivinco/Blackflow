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
__author__ = 'alivinco'


def sigterm_handler(signum, frame):
        log.info("Received signal #%d: %s. Shutting down service" % (signum, frame))
        service_manager.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--conf', help='Config file path')
    parser.add_argument('-a','--apps', help='Apps storage folder')
    args = parser.parse_args()
    with open(args.conf, "r") as app_file:
                    configs = json.loads(app_file.read())
    instance_name = configs["instance_config"]["name"]
    blackflow.configs.log.config["handlers"]["info_file_handler"]["filename"] = os.path.join(configs["log_dir"],"blackflow_info.log")
    blackflow.configs.log.config["handlers"]["error_file_handler"]["filename"] = os.path.join(configs["log_dir"],"blackflow_error.log")
    logging.config.dictConfig(blackflow.configs.log.config)

    log = logging.getLogger("bf_service")

    service_manager = ServiceManager("main")
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)
    adapters = []
    log.info("Starting application.Blackflow instance name = %s"%instance_name)
    context = BfContext()

    mqtt_adapter_service = MqttAdapter(context,instance_name,client_id=instance_name,host=configs["mqtt"]["host"],port=configs["mqtt"]["port"])
    adapters.append(mqtt_adapter_service)
    sys.path.append(args.apps.replace("apps",""))
    app_manager = AppManager(context,adapters,args.apps,configs=configs)
    rule_runner_service = AppRunner(context,adapters,app_manager)
    api_mqtt_handler = ApiMqttHandler(app_manager,mqtt_adapter_service,context,instance_name)
    mqtt_adapter_service.set_api_handler(api_mqtt_handler)

    service_manager.register(rule_runner_service)
    service_manager.register(mqtt_adapter_service)

    # service = ServiceRunner(RuleRunner(context))
    service_manager.start()
    service_manager.waitStartup(10)
    # app manager and api ghandler can be initialized only when mqtt adapter is running.
    app_manager.start_apps()
    api_mqtt_handler.start()

    while service_manager.getState()==ServiceState.RUN:
        time.sleep(1)
    if not service_manager.waitShutdown(10):
        log.error("Service Manager was not able to shut down all services in time. Unclean Shutdown !!!")
