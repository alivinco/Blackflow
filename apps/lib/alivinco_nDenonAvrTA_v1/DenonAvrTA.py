from blackflow.core.app import BfApp
import socket
import logging
log = logging.getLogger("DenonAvrTA")


class DenonAvrTA(BfApp):
    name = __name__

    def on_install(self):
        """
        Invoked once after app installation . Can be used to init application resources
        """
        log.info("%s app was installed ")

    def on_uninstall(self):
        """
        Invoked once before app uninstall  . Can be used to clean up application resources
        """
        log.info("%s app was uninstalled ")

    def on_start(self):
        """
           The method is invoked once during app startup . Init all variables here
        """
        log.info("%s app was started ")
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (self.config_get("avr_address"),int(self.config_get("avr_port")))
        self.sock.connect(server_address)
        log.info("App connected to Denon AVR")

    def on_stop(self):
        """
           The method is invoked during app shutdown . Do all cleanup work here
        """
        log.info("%s app was stopped ")
        self.sock.close()
        log.info("App disconnected from Denon AVR")

    def on_message(self, topic, iot_msg):
        """
          The method is invoked every time variable from sub_for section is changed (sub_for section in app config)
         """
        log.info("%s app was triggered by %s" % (self.name, topic))

        state = iot_msg.get_default_value()
        if state :
           cmd = "PWON\r"
        else:
           cmd = "PWSTANDBY\r"
        self.sock.sendall(cmd)
        # publish is a helper function for var_set.  First argument is publish destination alias and second is a payload



