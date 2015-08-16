import logging
from core.app import BfApp

log = logging.getLogger(__name__)

import pyfirmata

class ServoCam(BfApp):
    name = __name__
    def init_app(self):
        """

        """
        # don't forget to change the serial port to suit
        self.board = pyfirmata.Arduino('/dev/cu.usbmodem1411')
        log.info("Initializing Sevocam")
        addr = 2
        self.pins = {}
        self.pins[addr] = self.board.get_pin('d:%s:s'%addr)

    def run(self,triggered_by):
        log.info("%s app was triggered by %s"%(self.name,triggered_by))
        msg = self.var_get(triggered_by)["command"]
        value = msg["default"]["value"]
        servo_addr = int(msg["properties"]["address"])
        self.pins[servo_addr].write(int(value))




