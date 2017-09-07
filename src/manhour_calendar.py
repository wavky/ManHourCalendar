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
from itertools import chain
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
        self.weeks = []

    def initialize_days(self):
        # TODO: Cache update for a year, move update to outside the initialization
        holidays_one_year = update_holiday_schedule() or []
        # holidays_one_year = []
        self.holidays = list(filter(lambda ho: ho.month == str(self.index['month']), holidays_one_year))
        self.days = self.__dates2days()
        self.weeks = self.__days2weeks()

    @property
    def today(self):
        """
        :return: the Day object of today
        """
        index = self.dates.index(date.today())
        return self.days[index]

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
    def __init__(self, date_: date, holiday=None, dayoff=False, schedule=0, checkin=0, overtime=0, past=False):
        self.date = date_
        self.holiday = holiday
        self.is_dayoff = dayoff
        self.scheduled_work_hours = schedule
        self.checkin_manhour = checkin
        self.overtime = overtime
        self.is_past = past

    def checkin(self, hours=0, past=True):
        """
        Check in the man hours today.

        :param hours: man hours today
        :param past: if work today has done or not
        :return:
        """
        self.is_dayoff = hours == 0
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
        # how many hours you have worked this month
        self.checkin_manhour = 0
        # how many hours last you need to work this month
        self.manhour_remain = 0
        # how many overhours you have done for now
        self.overhours = 0

    @property
    def dayoff_list(self):
        return list(filter(lambda day: day.is_dayoff, self.month.days))

    def adjust(self, *, day_off: [int] = ()):
        """
        Adjust the schedule by setting dates of dayoff.
        You can ONLY adjust the days that is not past.

        :param day_off: dates which is planing to take a day off, while minus means that day switches to on duty
        """
        if len(day_off) == 0:
            return

        dayoff = set(filter(lambda d: d > 0, day_off))
        onduty = set(abs(x) for x in filter(lambda d: d < 0, dayoff))

        invalid_dates = set(filter(lambda d: abs(d) > len(self.month.days), day_off))
        if len(invalid_dates) > 0:
            print("Parameter out of range of month: {0}".format(invalid_dates))
            return

        conflict_dates = set(filter(lambda d: d in onduty, dayoff))
        conflict_dates = [(d, -d) for d in conflict_dates]
        if len(conflict_dates) > 0:
            print("Parameter conflicts at: {0}".format(conflict_dates))
            return

        dayoff_days = {i: self.month.days[i] for i in dayoff}
        onduty_days = {i: self.month.days[i] for i in onduty}

        past_day = dict(filter(lambda index, day: day.is_past, chain(dayoff_days, onduty_days)))
        if len(past_day) > 0:
            print("Illegal past dates: {0}".format(past_day.keys()))
            return

        dayoff_days = dayoff_days.values()
        onduty_days = onduty_days.values()

        for day in dayoff_days:
            day.is_dayoff = True
        for day in onduty_days:
            day.is_dayoff = False

        self.schedule()

    def schedule(self):
        # FIXME: 要可以指定安排工时精度
        days_past = set(filter(lambda day: day.is_past, self.month.days))
        days_remain = set(self.month.days) - days_past
        workdays_remain = set(filter(lambda day: not day.is_dayoff, days_remain))
        dayoff_remain = days_remain - workdays_remain

        if len(days_past) > 0:
            self.checkin_manhour = reduce(lambda a, b: a + b, [day.checkin_manhour for day in days_past])
        else:
            self.checkin_manhour = 0
        delta_manhour_remain = self.job.required_manhour - self.checkin_manhour
        self.manhour_remain = delta_manhour_remain if delta_manhour_remain > 0 else 0
        self.overhours = -delta_manhour_remain if delta_manhour_remain < 0 else 0

        if self.manhour_remain > 0:
            avg_manhour_remain = round(self.manhour_remain / len(workdays_remain), 2)
            if avg_manhour_remain >= self.job.daily_work_hours:
                if avg_manhour_remain <= self.job.daily_work_hours + self.job.max_daily_overhours:
                    schedule_hours = avg_manhour_remain
                else:
                    schedule_hours = self.job.daily_work_hours + self.job.max_daily_overhours
            else:
                schedule_hours = self.job.daily_work_hours
        else:
            schedule_hours = self.job.daily_work_hours

        for day in workdays_remain:
            day.schedule(schedule_hours)
            day.overtime = 0 if schedule_hours <= self.job.daily_work_hours \
                else round(schedule_hours - self.job.daily_work_hours, 2)
        for day in dayoff_remain:
            day.schedule(0)
            day.overtime = 0


class MHCalendarDrawer:
    """
    Output a monthly calendar.
    """

    def __init__(self, width=14):
        """

        :param width: minimum width is limited to 12, and MUST BE set as EVEN
        """
        self.width = 12 if width < 12 else width
        self.hr_line = '-' * (width + 1) * 7 + '-'
        self.seperator = '|' + ('-' * width + '|') * 7
        self.blank_line = str(' ' * ((width + 1) * 7 + 1))

    def __separate_line(self, week: str, end=''):
        week = ''.join(list(week).copy())
        distance_to_end = self.width * 7 + 8 - len(week)
        week += ' ' * distance_to_end
        week = list(week)
        week[::self.width + 1] = list('|' * 8)
        return ''.join(week) + end

    def __pipe(self, start, width, *texts, seperator='|', end=''):
        """
        The real name is Pile In piPE :P

        :param start: offset to start
        :param width: pipe's width
        :param texts: text to fill into a pipe
        :param seperator: seperator before and after, not count in pipe's width
        :return: a bamboo...
        """
        elements = [' ' * start, seperator]
        for t in texts:
            lent = len(t)
            if lent < width:
                t += ' ' * (width - lent)
            t += seperator
            elements.append(t)
        elements.append(end)
        return ''.join(elements)

    def __packup_week_schedule(self, week):
        first_weekday = week[0].date.weekday()
        start_index = first_weekday * (self.width + 1)
        pipes = list()

        pipes.append(
            self.__separate_line(
                self.__pipe(
                    start_index, self.width,
                    *['* Holiday *'.center(self.width) if week[i].holiday is not None else ' ' * self.width
                      for i in range(len(week))]), '\n'))
        pipes.append(
            self.__separate_line(
                self.__pipe(start_index, self.width, *['Schedule: ' + str(week[i].scheduled_work_hours)
                                                       for i in range(len(week))]), '\n'))
        pipes.append(
            self.__separate_line(
                self.__pipe(start_index, self.width, *['Overtime: ' + str(week[i].overtime)
                                                       for i in range(len(week))]), '\n'))
        pipes.append(
            self.__separate_line(
                self.__pipe(start_index, self.width, *['Checkin:  ' + str(week[i].checkin_manhour)
                                                       for i in range(len(week))]), '\n'))
        pipes.append(
            self.__separate_line(
                self.__pipe(start_index, self.width, *['Dayoff: ' + ('Yes' if week[i].is_dayoff else 'No')
                                                       for i in range(len(week))]), '\n'))
        pipes.append(
            self.__separate_line(
                self.__pipe(start_index, self.width, *['Done: ' + ('Yes' if week[i].is_past else 'No')
                                                       for i in range(len(week))]), '\n'))
        return pipes

    def draw(self, schedule: Schedule):
        cal = str(calendar.month(schedule.month.index['year'], schedule.month.index['month'], self.width))
        cal_lines = [' ' + w for w in cal.splitlines() if w != '']

        title = cal_lines.pop(0)
        day_of_week = cal_lines.pop(0)
        cal_weeks = cal_lines

        print('', title, self.hr_line, day_of_week, self.__separate_line(self.hr_line), sep='\n')
        for i in range(len(cal_weeks)):
            print(self.__separate_line(cal_weeks[i]))
            print(*self.__packup_week_schedule(schedule.month.weeks[i]), sep='', end='')
            print(self.__separate_line(self.hr_line))
            # TODO: 打印Job信息，本月工作时间概览，预期工资，节日列表，今日日期


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
