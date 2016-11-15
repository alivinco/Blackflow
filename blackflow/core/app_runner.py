from Queue import Queue, Empty
from blackflow.libs.thread_pool import ThreadPool
from threading import Thread
__author__ = 'alivinco'
from libs import logger
log = logger.getLogger("app_runner")


class AppRunner(Thread):
    def __init__(self, context,adapters,app_manager):
        # threading.Thread.__init__ (self)
        super(AppRunner, self).__init__(name = self.__class__.__name__)
        self.configured_app_instances = app_manager.get_app_instances()
        self.context_change_queue = Queue()
        self.app_manager = app_manager
        self.is_running = True
        self.is_stopped = False
        self.app_execution_thread_pool = ThreadPool(5)
        context.on_context_change = self.on_context_change
        self.context = context
        self.adapters = adapters

    def initialize(self):
        log.info("***Initializing app_instances runner service....")

    def on_context_change(self, var_name):
        """
        THe method should be called by context whenever context variable is changed
        :param var_name: variable name
        """
        self.context_change_queue.put(var_name)

    def stop(self):
        self.is_stopped = True

    def run(self):
        while not self.is_stopped:
            try:
                change_var_name = self.context_change_queue.get(timeout=2)
            except Empty:
                continue
            log.debug("config app instance size %s"%len(self.configured_app_instances))
            for app in self.configured_app_instances:
                if len(filter(lambda item : change_var_name == item["topic"], app.sub_for.values()))>0:
                    try:
                            log.debug("Adding task to the queue for app = %s" % app.alias)
                            self.context.analytics.tick_link_counter(change_var_name,app.alias)
                            self.app_execution_thread_pool.add_task(app.on_message, change_var_name, self.context.get(change_var_name))
                    except Exception as ex:
                        log.debug("App check method has failed with exception:")
                        log.exception(ex)
        log.info("Apps runner main loop stopped.")
