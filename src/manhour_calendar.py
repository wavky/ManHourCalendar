#!/usr/bin/env python3
# @Time    : 17-9-2 14:47
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : manhour_calendar.py

"""
Process overall information of one month.
"""

from collections import namedtuple
from datetime import datetime, timezone, timedelta
from urllib import request


class MonthlyCalendar:
    pass


class Day:
    def __init__(self, date: datetime, holiday=None, dayoff=False, schedule=0, checkin=0, past=False):
        self.date = date
        self.is_holiday = holiday
        self.is_dayoff = dayoff
        self.scheduled_work_hours = schedule
        self.checkin_manhour = checkin
        self.is_past = past

    def checkin(self, hours, past=True):
        """
        Check in the man hours today.

        :param hours: man hours today
        :param past: if work today has done or not
        :return:
        """
        self.is_dayoff = False
        self.checkin_manhour = hours
        self.is_past = past

    def dayoff(self):
        self.is_dayoff = True
        self.checkin_manhour = 0
        self.is_past = True



Holiday = namedtuple('Holiday', ('year', 'month', 'day', 'year_name', 'year_count', 'weekday', 'weekday_number', 'name'))

def current_date():
    return datetime.now(tz=timezone(timedelta(hours=+9), 'Tokyo'))

def update_holiday_schedule():
    """
    request new schedule list of holidays this year.

    :return: new list of Holiday or None for update failure.
    """

    url = "http://calendar-service.net/cal?start_year={year}&start_mon=1&end_year={year}&end_mon=12\
&year_style=normal&month_style=numeric&wday_style=en&format=csv&holiday_only=1"\
.format(year=current_date().year)
    print('Accessing network...')
    print('url: '+url)

    try:
        with request.urlopen(url) as f:
            content = [line.decode('EUC-JP').replace('\n', '') for line in f.readlines()]
            del content[0]
            content = [line.split(',') for line in content]
            holidays = [Holiday(*line) for line in content]
            print('Update success.')
            return holidays
    except:
        print("Update failure.")
        return None
