from datetime import datetime, tzinfo

import pytz


def get_server_timezone() -> tzinfo:
    # return pytz.timezone('America/Los_Angeles')
    return pytz.timezone('PST8PDT')


def get_server_now() -> datetime:
    tz = get_server_timezone()
    return datetime.now(tz)
