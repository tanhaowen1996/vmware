
import logging

from pytz import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy_dlock import create_sadlock

from app.container import Container
from app.settings import TIME_ZONE

from .tasks import do_vms_sync


LOG = logging.getLogger(__name__)


_container = Container()


def _create_scheduler() -> BlockingScheduler:
    job_stores = {
        'default': SQLAlchemyJobStore(engine=_container.db().engine),
    }
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }
    job_defaults = {
        'coalesce': True,
        'max_instances': 1
    }
    return BlockingScheduler(jobstores=job_stores,
                             executors=executors,
                             job_defaults=job_defaults,
                             timezone=timezone(TIME_ZONE))


scheduler = _create_scheduler()


def _wrapped_sync_vms_job():
    LOG.info("Start wrap sync vms job...")
    do_vms_sync(vm_service=_container.vm_service())
    LOG.info("Finished wrap sync vms job...")


def _show_jobs_job():
    LOG.info("Show current jobs saved...")
    for job in scheduler.get_jobs():
        LOG.info("saved job: %s" % job)


def scheduler_start():
    LOG.info("Start scheduler...")

    LOG.info("Add wrapped_sync_vms_job run every day at 2:30:05...")
    scheduler.add_job(_wrapped_sync_vms_job,
                      id='do_sync_vms_every_day_job',
                      replace_existing=True,
                      trigger='cron', second=5, minute=30, hour=2)

    LOG.info("Add wrapped_sync_vms_job run immediately after start...")
    scheduler.add_job(_wrapped_sync_vms_job,
                      id='do_sync_vms_immediately_job',
                      replace_existing=True,
                      trigger='date')

    LOG.info("Add show_jobs_job run every 120s")
    scheduler.add_job(_show_jobs_job,
                      id='show_jobs_every_2_minute_job',
                      replace_existing=True,
                      trigger='cron', minute='*/2')

    try:
        LOG.info("Start to scheduling jobs...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


key = "user/001"


def scheduler_start_with_dlock():
    with _container.db().session() as session:
        LOG.info("Waiting to Acquire lock, until get it...")
        with create_sadlock(session, key):
            LOG.info("Acquired lock start to running...")
            scheduler_start()
        LOG.info("Released lock...")
