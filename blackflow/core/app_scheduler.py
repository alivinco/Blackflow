from apscheduler.schedulers.background import BackgroundScheduler
from libs import logger
import copy
log = logger.getLogger("bf_app_scheduler")


class AppScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})

    def init_scheduler(self):
        self.scheduler.start()

    def init_schedule(self, inst_config , app_inst):
        self.remove_schedules_for_instance(inst_config["id"])
        for sch in inst_config["schedules"]:
            if "name" in sch:
                sch = copy.deepcopy(sch)
                sch_id = "%s_%s"%(inst_config["id"],sch["name"])
                sch_name = "scheduler:%s"%sch["name"]
                sch_trigger_type = sch["trigger_type"]
                del sch["name"]
                del sch["trigger_type"]
                log.debug("Adding scheduler id = %s , name = %s , trigger = %s , params = %s "%(sch_id, sch_name, sch_trigger_type, sch))
                self.scheduler.add_job(app_inst.on_message,sch_trigger_type, id=sch_id, args=[sch_name, None], **sch)
            else:
                log.error("Schedule without name is not allowed")

    def remove_schedules_for_instance(self, inst_id):
        # filtering out all the jobs relevant to particular instance
        jobs = filter(lambda job : "%s_"%inst_id in job.id , self.scheduler.get_jobs())
        for job in jobs:
            self.scheduler.remove_job(job.id)
            log.debug("Job with id = %s was removed from scheduler")