import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .dates import EASTERN_STANDARD_TIME

"""
Simple wrapper class to wire up cron 
and interval tasks with AsyncIoScheduler
"""
class DaemonHelper:
    # create a simple job
    # with available kwargs from the scheduler
    @staticmethod
    def add(job_fn, **kwargs) -> None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(job_fn, misfire_grace_time=120, timezone=EASTERN_STANDARD_TIME, **kwargs)
        scheduler.start()

        if not scheduler.running:
            asyncio.get_event_loop().run_forever()

        
    # create a simple job
    # with available kwargs from the scheduler
    @staticmethod
    def add_minute_interval(job_fn, minutes: int) -> None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(job_fn, misfire_grace_time=120, timezone=EASTERN_STANDARD_TIME, trigger="interval", minutes=minutes)
        scheduler.start()

        if not scheduler.running:
            asyncio.get_event_loop().run_forever()