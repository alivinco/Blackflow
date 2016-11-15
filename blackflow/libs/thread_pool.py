from Queue import Queue
from threading import Thread
from libs import logger
__author__ = 'alivinco'
log = logger.getLogger("thread_pool")

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks,do_and_die=False):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.do_and_die = do_and_die
        self.start()

    def run(self):
        log.info("Thread %s was added to the pool.Do and die = %s "%(self.getName(),self.do_and_die))
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except :
                log.exception("Thread pool worker %s. Task crashed with exception:"%self.getName())

            self.tasks.task_done()
            if self.do_and_die : break


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads,max_size=20,min_worker_queue_size_before_extension=1):
        self.tasks = Queue()
        self.pool_min_size = num_threads
        self.pool_max_size = max_size
        self.min_worker_queue_size_before_extension = min_worker_queue_size_before_extension

        # self.max_size =
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""

        self.tasks.put((func, args, kargs))
        """ If Queue size is more then 0 it means all workers are busy and we need to add one short living thread"""
        if self.tasks.qsize() > self.min_worker_queue_size_before_extension:
           # print "addind new task to queue , queue size is %s"%(self.tasks.qsize())
           Worker(self.tasks,do_and_die=True)


    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

if __name__ == '__main__':
    from random import randrange
    delays = [randrange(1, 10) for i in range(100)]

    from time import sleep
    def wait_delay(d):
        print 'sleeping for (%d)sec' % d
        sleep(d)

    # 1) Init a Thread pool with the desired number of threads
    pool = ThreadPool(50)

    for i, d in enumerate(delays):
        # print the percentage of tasks placed in the queue
        #print '%.2f%c' % ((float(i)/float(len(delays)))*100.0,'%')

        # 2) Add the task to the queue
        d = 0.0001
        pool.add_task(wait_delay, d)

    # 3) Wait for completion
    pool.wait_completion()
