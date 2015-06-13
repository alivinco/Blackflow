
import signal
import time
from adapters.mqtt_adapter import MqttAdapter
from core.app_manager import AppManager
from core.app_runner import AppRunner
from handlers.api_mqtt_handler import ApiMqttHandler
from libs.context import BfContext

__author__ = 'alivinco'
from smartlylib.service.Service import ServiceRunner, Service, ServiceManager, ServiceState
import logging, logging.config
import configs.log

logging.config.dictConfig(configs.log.config)
log = logging.getLogger("bf_rules_runner")



# class BlackflowService(Service):
#     def __init__(self,context):
#         super(BlackflowService, self).__init__(self.__class__.__name__)
#         self.context = context
#
#     def initialize(self):
#         log.info("***Initializing application.....")
#
#     def run(self):
#         pass

def sigterm_handler(signum, frame):
        log.info("Received signal #%d: %s. Shutting down service" % (signum, frame))
        service_manager.stop()

if __name__ == "__main__":
    service_manager = ServiceManager("main")
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)
    adapters = []
    log.info("Starting application")
    context = BfContext()

    mqtt_adapter_service = MqttAdapter(context)
    adapters.append(mqtt_adapter_service)
    app_manager = AppManager(context,adapters)
    rule_runner_service = AppRunner(context,adapters,app_manager)
    api_mqtt_handler = ApiMqttHandler(app_manager,mqtt_adapter_service)
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
