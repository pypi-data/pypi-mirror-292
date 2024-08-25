import time
import datetime

__all__ = [
    'now',
    'now_str',
    'datetime_to_timestamp',
    'timestamp_to_datetime',
]


def now(unit: str = 's'):
    """
    get current timestamp

    :param unit: s or ms
    :return: current timestamp
    """
    if unit not in ('s', 'ms'):
        raise Exception('invalid params: unit not in (\'s\',\'ms\')')

    ts = time.time()
    if unit == 's':
        return int(ts)
    if unit == 'ms':
        return int(ts * 1000)


def now_str(fmt: str = '%Y-%m-%d %H:%M:%S'):
    """
    get formatted datetime string of current timestamp

    :param fmt: format of datetime
    :return: formatted datetime string
    """
    return datetime.datetime.now().strftime(fmt)


def datetime_to_timestamp(dt: str, fmt: str = '%Y-%m-%d %H:%M:%S'):
    """
    convert formatted datetime string to timestamp(unit: s)

    :param dt: datetime string
    :param fmt: format of datetime
    :return: timestamp(unit: s)
    """
    time_array = time.strptime(dt, fmt)
    return int(time.mktime(time_array))


def timestamp_to_datetime(ts: int, fmt: str = '%Y-%m-%d %H:%M:%S'):
    """
    convert timestamp(unit: s) to formatted datetime string

    :param ts: timestamp(unit: s)
    :param fmt: format of datetime
    :return: formatted datetime string
    """
    time_local = time.localtime(ts)
    return time.strftime(fmt, time_local)
