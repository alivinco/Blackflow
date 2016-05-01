import logging
from blackflow.core.app import BfApp
import pyfirmata
log = logging.getLogger(__name__)


class ServoCam(BfApp):
    name = __name__

    def on_start(self):
        """

        """
        # don't forget to change the serial port to suit
        self.board = pyfirmata.Arduino('/dev/cu.usbmodem1411')
        log.info("Initializing Sevocam")
        addr = 2
        self.pins = {}
        self.pins[addr] = self.board.get_pin('d:%s:s'%addr)

    def on_message(self,topic,iot_msg):
        log.info("%s app was triggered by %s"%(self.name,topic))
        value = iot_msg.get_default_value()
        servo_addr = int(iot_msg.get_properties()["address"])
        self.pins[servo_addr].write(int(value))




