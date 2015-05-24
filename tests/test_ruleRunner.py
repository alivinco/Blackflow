from time import sleep
from unittest import TestCase
from smartlylib.service.Service import ServiceRunner
from adapters.mqtt_adapter import MqttAdapter
from core.rule_runner import RuleRunner
from libs.context import BfContext

__author__ = 'alivinco'

import logging, logging.config
import configs.log

logging.config.dictConfig(configs.log.config)

class TestRuleRunner(TestCase):

    def setUp(self):
        self.context = BfContext()
        self.mqtt_adapter_service = MqttAdapter(self.context)
        self.rule_runner = RuleRunner(self.context,[self.mqtt_adapter_service])

    # def test_load_rules(self):
    #     self.rule_runner.load_rules()

    def test_run(self):

        # self.rule_runner.load_rules()
        sr = ServiceRunner(self.rule_runner)
        sr.start()
        sr2 = ServiceRunner(self.mqtt_adapter_service)
        sr2.start()
        sleep(1)
        self.context.set("home",{"mode":"at_home"})
        self.context.set("mqtt:/dev/zw/75/bin_motion/1/events",{"event":{"default":{"value":True}}})
        sleep(1)

        sr.stop()
        sr2.stop()