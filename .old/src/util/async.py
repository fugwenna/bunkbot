import asyncio
from src.util.helpers import EST
from apscheduler.schedulers.asyncio import AsyncIOScheduler

"""
Simple wrapper class to wire up cron 
and interval tasks with AsyncIoScheduler
"""
class AsyncSchedulerHelper:
    # create a simple job
    # with available kwargs from the scheduler
    @staticmethod
    def add_job(job_fn, **kwargs) -> None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(job_fn, misfire_grace_time=120, timezone=EST, **kwargs)
        scheduler.start()

        if not scheduler.running:
            asyncio.get_event_loop().run_forever()