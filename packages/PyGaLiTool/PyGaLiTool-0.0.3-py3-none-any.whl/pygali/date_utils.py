import datetime
from typing import Union

import pytz
from enum import Enum


class DatetimeEnum(Enum):
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_datetime_fmt(fmt):
    """
    如果是枚举类,获取value
    否则就原样返回
    :param fmt:
    :return:
    """
    if isinstance(fmt, Enum):
        return fmt.value
    else:
        return fmt


def cur_date(fmt: Union[DatetimeEnum, str] = DatetimeEnum.DATE_FORMAT) -> str:
    """
    获取当前时区的Date
    :param fmt:
    :return:
    """
    fmt = get_datetime_fmt(fmt)
    return datetime.date.today().strftime(fmt)


def cur_datetime(fmt: Union[DatetimeEnum, str] = DatetimeEnum.DATETIME_FORMAT) -> str:
    """
    获取当前时区的DateTime
    :param fmt:
    :return:
    """
    fmt = get_datetime_fmt(fmt)
    return datetime.datetime.strftime(datetime.datetime.now(), fmt)


def cur_datetime_tz(time_zone: str, fmt: Union[DatetimeEnum, str] = DatetimeEnum.DATETIME_FORMAT) -> str:
    """
    获取指定时区的DateTime
    :param time_zone:
    :param fmt:
    :return:
    """
    fmt = get_datetime_fmt(fmt)
    if time_zone.startswith("GMT"):
        time_zone = 'Etc/' + time_zone
    return datetime.datetime.strftime(datetime.datetime.now(tz=pytz.timezone(time_zone)), fmt)


def date_add(date_str: str, days: int, fmt=DatetimeEnum.DATE_FORMAT) -> str:
    """
    DATE_ADD: 向日期加上指定的时间间隔
    :param date_str: 当前日期(%Y-%m-%d 格式的str)
    :param days: 相加天数
    :param fmt: 日期格式,默认为"%Y-%m-%d"
    :return: 当前日期 + 指定天数
    """
    fmt = get_datetime_fmt(fmt)
    dt: datetime = datetime.datetime.strptime(date_str, fmt) + datetime.timedelta(days=days)
    return dt.strftime(fmt)


def date_sub(date_str: str, days: int, fmt=DatetimeEnum.DATE_FORMAT) -> str:
    """
    DATE_SUB: 向日期减去指定的时间间隔
    :param date_str: 当前日期(%Y-%m-%d 格式的str)
    :param days: 相加天数
    :param fmt: 日期格式,默认为"%Y-%m-%d"
    :return: 当前日期 + 指定天数
    """
    fmt = get_datetime_fmt(fmt)
    dt: datetime = datetime.datetime.strptime(date_str, fmt) - datetime.timedelta(days=days)
    return dt.strftime(fmt)


if __name__ == '__main__':
    print(cur_date())
    print(cur_date("%Y%m%d"))
    print(cur_datetime())
    print(cur_datetime("%Y%m%d%H%M%S"))
    print(date_sub(cur_date(), 1))
    print(date_add(cur_date(), -1))
    print(date_add(cur_date(), 1))
    print(cur_datetime_tz("GMT-2"))
    print(cur_datetime_tz("GMT-8"))
