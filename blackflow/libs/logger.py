import logging
import logging.handlers
import Queue
import threading

log_queue = Queue.Queue()
logger = logging.getLogger("bf")
log_writer = logging.getLogger("writer")
is_running = True


# Should be invoked from main process .
def configure(log_file="info.log",logging_level=logging.INFO,enable_console=False):
    global queue_handler , log_writer
    queue_handler = QueueHandler(log_queue)
    logger.setLevel(logging_level)
    logger.addHandler(queue_handler)
    handler = logging.handlers.RotatingFileHandler(log_file, 'a', 400000, 2)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(name)s %(lineno)d %(message)s :')
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    log_writer.addHandler(handler)
    if enable_console:
        log_writer.addHandler(console_handler)
    writer_thread = threading.Thread(target=run_queue_handler)
    writer_thread.start()


def getLogger(name=None):
    if not name:
        name = "default"
    return logging.getLogger("bf."+name)


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
