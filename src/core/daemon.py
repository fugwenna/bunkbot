import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .dates import EASTERN_STANDARD_TIME

class DaemonHelper:
    """
    Simple wrapper class to wire up cron 
    and interval tasks with AsyncIoScheduler
    """

    @staticmethod
    def add(job_fn, **kwargs) -> None:
        """
        Create a simple job with available kwargs from the scheduler

        Parameters
        -----------
        **kwargs: any
            Keyword arguments to align with the async schedular
        """
        scheduler = AsyncIOScheduler()
        scheduler.add_job(job_fn, misfire_grace_time=None, timezone=EASTERN_STANDARD_TIME, **kwargs)
        scheduler.start()

        if not scheduler.running:
            asyncio.get_event_loop().run_forever()

        
    @staticmethod
    def add_minute_interval(job_fn, minutes: int) -> None:
        """
        Create a simple job with a function for the scheduler 
        and the amount of minutes to wait to run again

        Parameters
        -----------
        job_fn: Function
            Function that will run on each interval

        minutes: int
            Amount of minutes to wait until executing the job_fn again
        """
        scheduler = AsyncIOScheduler()
        scheduler.add_job(job_fn, misfire_grace_time=None, timezone=EASTERN_STANDARD_TIME, trigger="interval", minutes=minutes)
        scheduler.start()

        if not scheduler.running:
            asyncio.get_event_loop().run_forever()
