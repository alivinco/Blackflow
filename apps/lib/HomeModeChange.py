import logging
from core.app import BfApp

__author__ = 'alivinco'

log = logging.getLogger("HomeModeChange")

class HomeModeChange(BfApp):

    name = "HomeModeChange"
    subscribe_for = ["lights_state"]

    def run(self):
        log.info("Lights off ")
        self.context.set("home_mode", "sleep", self)
        log.info("Home mode was changed to 'sleep' ")





