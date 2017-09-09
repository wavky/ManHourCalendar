#!/usr/bin/env python3
# @Time    : 17-9-2 14:47
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : time_elements.py

"""
Process overall information of one month.
"""
import calendar
from collections import namedtuple
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from functools import reduce
from urllib import request

from mhcalendar.job import Job

Holiday = namedtuple('Holiday',
                     ('year', 'month', 'day', 'year_name', 'year_count', 'weekday', 'weekday_number', 'name'))


class Month:
    def __init__(self, year, month):
        self.index = {'year': year, 'month': month}
        self.dates = list(
            filter(lambda date_: date_.month == month, calendar.Calendar().itermonthdates(year, month)))
        self.days = []
        self.holidays = []
        self.weeks = []

    def initialize_days(self):
        # TODO: Cache update for a year, move update to outside the initialization
        # holidays_one_year = update_holiday_schedule() or []
        holidays_one_year = []
        self.holidays = list(filter(lambda ho: ho.month == str(self.index['month']), holidays_one_year))
        self.days = self.__dates2days()
        self.weeks = self.__days2weeks()

    @property
    def today(self):
        """
        :return: the Day object of today, or None if today is not in this month
        """
        td = date.today()
        if td in self.dates:
            index = self.dates.index(td)
            return self.days[index]

    @property
    def next_day(self):
        """
        Obtain the next day that is not past.

        :return: object Day or None
        """
        for day in self.days:
            if not day.is_past:
                return day

    def __dates2days(self):
        """
        adapt dates to days

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

    def __days2weeks(self):
        today = date.today()
        date_matrix = calendar.Calendar().monthdayscalendar(today.year, today.month)
        date_list = list(filter(lambda d: d > 0, calendar.Calendar().itermonthdays(today.year, today.month)))
        weeks = []
        for w in date_matrix:
            week = []
            weeks.append(week)
            for d in w:
                if d > 0:
                    week.append(self.days[date_list.index(d)])
        return weeks

    def __str__(self):
        return "MonthlyCalendar({year}, {month} days: {days})".format(year=self.index['year'],
                                                                      month=self.index['month'],
                                                                      days=self.days)

    def __repr__(self):
        return self.__str__()


class Day:
    def __init__(self, date_: date, holiday: Holiday = None, dayoff=False,
                 schedule=0, checkin=0, overtime=0, past=False):
        self.date = date_
        self.holiday = holiday
        self.is_dayoff = dayoff
        self.scheduled_work_hours = schedule
        self.checkin_manhour = checkin
        # overtime at past day stands for OT indeed, otherwise it only stands for scheduled-OT
        self.overtime = overtime
        self.is_past = past

    def checkin(self, hours=0, past=True):
        """
        Check in the man hours of this day.

        :param hours: man hours today, default 0 means check in as scheduled manhour
        :param past: if work today has done or not
        """
        self.checkin_manhour = hours if hours > 0 else self.scheduled_work_hours
        if past:
            self.overtime -= self.scheduled_work_hours - self.checkin_manhour
        self.is_past = past

    def dayoff(self):
        """
        You should only set day off the day which is NOT past.
        """
        self.is_dayoff = True
        self.checkin_manhour = 0
        self.schedule(0)
        self.overtime = 0

    def schedule(self, hours=0):
        """
        You should only schedule a day that is NOT past.

        :param hours:
        """
        self.scheduled_work_hours = hours

    def __str__(self):
        return "Day({date}, holiday={holiday}, dayoff={dayoff}, " \
               "scheduled={scheduled}, checkin={checkin}, past={past})" \
            .format(date=self.date, holiday=self.holiday, dayoff=self.is_dayoff,
                    scheduled=self.scheduled_work_hours, checkin=self.checkin_manhour, past=self.is_past)

    def __repr__(self):
        return self.__str__()


class Schedule:
    def __init__(self, job: Job, month: Month):
        self.job = job
        self.month = month
        # how many hours you have worked this month (Decimal type or 0)
        self.checkin_manhour = 0
        # how many hours last you need to work this month (Decimal type or 0)
        self.manhour_remain = 0
        # how many overhours you have done for now (Decimal type or 0)
        self.overhours = 0
        # hours that CAN NOT be scheduled on this month
        self.manhour_absence = 0

    @property
    def dayoff_list(self):
        return list(filter(lambda day: day.is_dayoff, self.month.days))

    def adjust(self, *, day_off: [int] = ()):
        """
        Adjust the schedule by setting dates of dayoff.
        You can ONLY adjust the days that is not past.
        You need to re-schedule it before draw().

        :param day_off: dates which is planing to take a day off, while minus means that day switches to on duty
        """
        if len(day_off) == 0:
            return

        dayoff = sorted(set(filter(lambda d: d > 0, day_off)))
        onduty = sorted(set(abs(x) for x in filter(lambda d: d < 0, day_off)))

        invalid_dates = sorted(set(filter(lambda d: abs(d) > len(self.month.days) or d == 0, day_off)))
        if len(invalid_dates) > 0:
            print("Parameter out of range of month: {0}".format(invalid_dates))
            return

        conflict_dates = sorted(set(filter(lambda d: d in onduty, dayoff)))
        conflict_dates = [(d, -d) for d in conflict_dates]
        if len(conflict_dates) > 0:
            print("Parameter conflicts at: {0}".format(conflict_dates))
            return

        dayoff_days = {date: self.month.days[date - 1] for date in dayoff}
        onduty_days = {date: self.month.days[date - 1] for date in onduty}

        past_day = dict(filter(lambda item: item[1].is_past, dayoff_days.items()))
        past_day.update(dict(filter(lambda item: item[1].is_past, onduty_days.items())))
        if len(past_day) > 0:
            print("Illegal past dates: {0}".format(list(past_day.keys())))
            return

        dayoff_days = dayoff_days.values()
        onduty_days = onduty_days.values()

        for day in dayoff_days:
            day.dayoff()
        for day in onduty_days:
            day.is_dayoff = False

    @classmethod
    def __sort_day(cls, days):
        return sorted(days, key=lambda day: day.date)

    def __calculate_manhour_remain(self):
        days_past = set(filter(lambda day: day.is_past, self.month.days))
        days_remain = set(self.month.days) - days_past
        workdays_remain = set(filter(lambda day: not day.is_dayoff, days_remain))
        dayoff_remain = days_remain - workdays_remain

        if len(days_past) > 0:
            self.checkin_manhour = reduce(lambda a, b: a + b, [dec_float(day.checkin_manhour) for day in days_past])
            self.overhours = reduce(lambda a, b: a + b, [dec_float(day.overtime) for day in days_past])
        else:
            self.checkin_manhour = 0
            self.overhours = 0
        delta_manhour_remain = dec_float(self.job.required_manhour) - self.checkin_manhour
        self.manhour_remain = delta_manhour_remain if delta_manhour_remain > 0 else 0
        return self.__sort_day(workdays_remain), self.__sort_day(dayoff_remain), self.manhour_remain

    def __ceil_workhour_by_precision(self, workhour: Decimal, precision: Decimal):
        """
        make schedule time "ceil" to precision, only if it's not beyond the max overtime

        :param workhour:
        :param precision:
        :return: Decimal type
        """
        if precision > 0:
            if workhour % precision:
                pre_schedule_hours = (workhour // precision + 1) * precision
            else:
                pre_schedule_hours = workhour
        else:
            pre_schedule_hours = workhour

        max_daily_work_hours = dec_float(self.job.daily_work_hours) + dec_float(self.job.max_daily_overhours)
        pre_schedule_hours = max_daily_work_hours \
            if pre_schedule_hours > max_daily_work_hours else pre_schedule_hours

        return pre_schedule_hours

    def schedule(self, precision=1):
        """
        Update schedule time of workdays remaining.

        :param precision: minimum time unit to calculate the schedule time, default to 1 hour
        (eg. 0.25 means 15 mins). 0 means no limit.
        :return:
        """
        workdays_remain, dayoff_remain, manhour_remain = self.__calculate_manhour_remain()
        workdays_count = len(workdays_remain)

        print('workdays remaining:', workdays_count)
        for day in workdays_remain:

            print('date:', day.date, "\t manhour_remain:", manhour_remain)
            dec_daily_work_hours = dec_float(self.job.daily_work_hours)
            if manhour_remain > dec_daily_work_hours:
                avg_manhour_remain = Decimal(manhour_remain / workdays_count).quantize(Decimal('1.00'))
                workdays_count -= 1
                schedule_hours = self.__ceil_workhour_by_precision(avg_manhour_remain, dec_float(precision))
                print('daily_avg_manhour_remain:', avg_manhour_remain)
            else:
                schedule_hours = dec_daily_work_hours

            day.schedule(float(schedule_hours))
            if schedule_hours > dec_daily_work_hours:
                day.overtime = float(schedule_hours - dec_daily_work_hours)
            else:
                day.overtime = 0

            manhour_remain -= schedule_hours

            print("schedule_hours:", schedule_hours, "\t manhour_remain:", manhour_remain, '\n')

        for day in dayoff_remain:
            day.schedule(0)
            day.overtime = 0

        self.manhour_absence = float(manhour_remain) if manhour_remain > 0 else 0


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


def any(func, iterable):
    for x in iterable:
        if func(x):
            return True
    return False


def dec_float(number: float):
    return Decimal(str(number))
