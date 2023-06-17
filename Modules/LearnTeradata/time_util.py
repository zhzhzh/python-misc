import pytz
import datetime
import time

HOUR_FORMAT = '%Y-%m-%d %H:00:00'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y%m%d'

def get_server_timezone():
    # return pytz.timezone('America/Los_Angeles')
    return pytz.timezone('PST8PDT')


def get_server_now():
    tz = get_server_timezone()
    return datetime.datetime.now(tz)


def get_server_now_without_tz():
    tz = get_server_timezone()
    now = datetime.datetime.now(tz)
    return now.replace(tzinfo=None, microsecond=0)


def get_time_hour_str(time):
    return time.strftime(HOUR_FORMAT)


def get_time_date_str(time):
    return time.strftime(DATE_FORMAT)


def get_str_from_datetime(dt):
    return dt.strftime(TIME_FORMAT)


def get_timestamp_from_time_str(time_str):
    dt = datetime.datetime.strptime(time_str, TIME_FORMAT)
    ts = time.mktime(dt.timetuple())
    # print(time_str, dt, ts, int(ts))
    return int(ts)


def get_timestamp_from_datetime(dt):
    ts = time.mktime(dt.timetuple())
    return ts


def get_time_str_from_timestamp(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    time_str = dt.strftime(TIME_FORMAT)
    # print(ts, dt, time_str)
    return time_str


def get_time_from_str(date_str):
    if len(date_str) == 8:
        return datetime.date(
            year=int(date_str[0:4]),
            month=int(date_str[4:6]),
            day=int(date_str[6:8])
        )
    else:
        return datetime.datetime(
            year=int(date_str[0:4]),
            month=int(date_str[4:6]),
            day=int(date_str[6:8]),
            hour=int(date_str[8:10])
        )


def get_time_to_hour(dt):
    hour_dt = datetime.datetime(year=dt.year,
                                month=dt.month,
                                day=dt.day,
                                hour=dt.hour)
    return hour_dt