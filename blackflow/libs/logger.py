import logging
import logging.handlers
import Queue
import threading

log_queue = Queue.Queue()
logger = logging.getLogger("main")
log_writer = logging.getLogger("writer")
is_running = True
#logging.config.dictConfig(logconfig.config)


# Should be invoked from main process .
def configure(log_file="info.log"):
    global queue_handler , log_writer
    queue_handler = QueueHandler(log_queue)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(queue_handler)
    handler = logging.handlers.RotatingFileHandler(log_file, 'a', 300, 0)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(module)s %(name)s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    log_writer.addHandler(handler)
    log_writer.addHandler(console_handler)
    writer_thread = threading.Thread(target=run_queue_handler)
    writer_thread.start()


def getLogger(name=None):
    if not name:
        name = "default"
    return logging.getLogger("main."+name)


def stopLogger():
    global is_running
    is_running = False


class QueueHandler(logging.Handler):
    """
    This is a logging handler which sends events to a multiprocessing queue.

    The plan is to add it to Python 3.2, but this can be copy pasted into
    user code for use with earlier Python versions.
    """

    def __init__(self, queue):
        """
        Initialise an instance, using the passed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    def emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue.
        """
        try:
            ei = record.exc_info
            if ei:
                dummy = self.format(record) # just to get traceback text into record.exc_text
                #record.exc_info = None  # not needed any more
            self.queue.put_nowait(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def run_queue_handler():
    while is_running:
        try:
            record = log_queue.get(timeout=10)
            log_writer.handle(record)
        except Queue.Empty:
            pass
