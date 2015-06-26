from unittest import TestCase
from core.app_manager import AppManager
from libs.context import BfContext

__author__ = 'alivinco'


class TestAppManager(TestCase):
    def setUp(self):
        self.context = BfContext()
        self.app_manager = AppManager(BfContext, [])

    def test_load_app_descriptors(self):

        self.app_manager.load_app_descriptors()
        self.assertGreater(len(self.app_manager.app_descriptors),0,"Descriptor is empty")
        # self.fail()
