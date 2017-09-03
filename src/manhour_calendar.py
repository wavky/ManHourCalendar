#!/usr/bin/env python3
# @Time    : 17-9-2 14:47
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : manhour_calendar.py

"""
Process overall information of one month.
"""
import calendar
from collections import namedtuple
from datetime import date, datetime, timezone, timedelta
from functools import reduce
from urllib import request

from src.job import Job

Holiday = namedtuple('Holiday',
                     ('year', 'month', 'day', 'year_name', 'year_count', 'weekday', 'weekday_number', 'name'))


class Month:
    def __init__(self, year, month):
        self.index = {'year': year, 'month': month}
        self.dates = list(
            filter(lambda date_: date_.month == month, calendar.Calendar().itermonthdates(year, month)))
        self.days = []
        self.holidays = []

    def initialize_days(self):
        # TODO: Cache update for a year, move update to outside the initialization
        holidays_one_year = update_holiday_schedule() or []
        self.holidays = list(filter(lambda ho: ho.month == str(self.index['month']), holidays_one_year))
        self.days = self.__dates2days()

    def __dates2days(self):
        """
        adapt date list to day list

        :return: list of Day
        """

        days = []
        holidays = self.holidays.copy()
        for date_ in self.dates:
            holiday = None
            if len(holidays) > 0 and holidays[0].day == str(date_.day):
                holiday = holidays[0]
                del holidays[0]

            # weekday 5 means Saturday
            dayoff = holiday is not None or date_.weekday() >= 5
            days.append(Day(date_, holiday, dayoff))
        return days

    def __str__(self):
        return "MonthlyCalendar({year}, {month} days: {days})".format(year=self.index['year'],
                                                                      month=self.index['month'],
                                                                      days=self.days)

    def __repr__(self):
        return self.__str__()


class Day:
    def __init__(self, date_: date, holiday=None, dayoff=False, schedule=0, checkin=0, past=False):
        self.date = date_
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

    def schedule(self, hours=0):
        """
        You should only schedule a day that is NOT past.

        :param hours:
        :return:
        """
        self.scheduled_work_hours = hours

    def __str__(self):
        return "Day({date}, holiday={holiday}, dayoff={dayoff}, scheduled={scheduled}, checkin={checkin}, past={past})" \
            .format(date=self.date, holiday=self.is_holiday, dayoff=self.is_dayoff, scheduled=self.scheduled_work_hours,
                    checkin=self.checkin_manhour, past=self.is_past)

    def __repr__(self):
        return self.__str__()


class Schedule:
    def __init__(self, job: Job, month: Month):
        self.job = job
        self.month = month
        self.dayoff_list = list(filter(lambda day: day.is_dayoff, month.days))

    def adjust(self, dayoff: [int] = [], onduty: [int] = []):
        """
        adjust the schedule by setting dates of dayoff and/or on duty.

        :param dayoff: date list which planing to take a day off
        :param onduty: date list which planing to go to work
        """
        if dayoff == onduty == []:
            return
        elif dayoff == onduty:
            print("Parameter dayoff should NOT be same to onduty.")
            return
            # TODO: Continue...

    def schedule(self):
        days_past = list(filter(lambda day: day.is_past, self.month.days))
        days_remain = set(self.month.days) - set(days_past)
        workdays_remain = list(filter(lambda day: not day.is_dayoff, days_remain))

        checkin_manhour = reduce(lambda a, b: a + b, [day.checkin_manhour for day in days_past])
        manhour_remain = self.job.required_manhour - checkin_manhour

        # TODO: 未考虑加班时间上限
        avg_manhour_remain = round(manhour_remain / workdays_remain, 2)
        for day in workdays_remain:
            day.schedule(avg_manhour_remain)


class Calendar:
    """
    Output a monthly calendar.
    """
    pass


def timezone_date(tz=+9, area='Tokyo'):
    return datetime.now(tz=timezone(timedelta(hours=tz), area)).date()


def update_holiday_schedule():
    """
    request new schedule list of holidays this year.

    :return: new list of Holiday or None for update failure.
    """

    url = "http://calendar-service.net/cal?start_year={year}&start_mon=1&end_year={year}&end_mon=12\
&year_style=normal&month_style=numeric&wday_style=en&format=csv&holiday_only=1".format(year=date.today().year)
    print('Accessing network...')
    print('url: ' + url)

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
