import datetime, pytz

EASTERN_STANDARD_TIME: str = "US/Eastern"
MDY_FORMATTED: str = "{0:%m/%d/%Y %I:%M:%S %p}"


def get_now(format_date: bool = True) -> any:
    """
    Get the current timestamp of "EST now"

    Parameters
    -----------
    formate_date: bool (default True)
        Format the date value

    Returns
    --------
    Current value of the current datetime
    """
    now = datetime.datetime.now(tz=pytz.timezone(EASTERN_STANDARD_TIME))

    if format_date:
        return MDY_FORMATTED.format(now)

    return now
