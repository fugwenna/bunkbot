import datetime, pytz

EASTERN_STANDARD_TIME: str = "US/Eastern"
MDY_FORMATTED: str = "{0:%m/%d/%Y %I:%M:%S %p}"


"""
Get the current timestamp 
"""
def get_now(format_date: bool = True):
    now = datetime.datetime.now(tz=pytz.timezone(EASTERN_STANDARD_TIME))

    if format_date:
        return MDY_FORMATTED.format(now)

    return now