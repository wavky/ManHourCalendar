#!/usr/bin/env python3
# @Time    : 17-9-8 23:48
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : io.py

"""
Process input and output
"""
import calendar
from datetime import date

from mhcalendar.time_elements import Schedule


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
        week = list(week)
        distance_to_end = self.width * 7 + 8 - len(week)
        week += list(' ' * distance_to_end)
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

        holidays = ['* Holiday *'.center(self.width)
                    if week[i].holiday is not None else ' ' * self.width for i in range(len(week))]
        schedule_hours = ['Sched: {}'.format(week[i].scheduled_work_hours)
                          if not week[i].is_dayoff else '-' for i in range(len(week))]
        overtime_hours = ['OT: {}'.format(week[i].overtime)
                          if not week[i].is_dayoff else '-' for i in range(len(week))]
        checkin_hours = ['Checkin: {}'.format(week[i].checkin_manhour)
                         if not week[i].is_dayoff else '-' for i in range(len(week))]
        dayoff = ['Dayoff: {}'.format('Yes' if week[i].is_dayoff else 'No') for i in range(len(week))]
        done = ['Done: {}'.format('Yes' if week[i].is_past else 'No') for i in range(len(week))]
        pipes.append(self.__separate_line(self.__pipe(start_index, self.width, *holidays), '\n'))
        pipes.append(self.__separate_line(self.__pipe(start_index, self.width, *schedule_hours), '\n'))
        pipes.append(self.__separate_line(self.__pipe(start_index, self.width, *overtime_hours), '\n'))
        pipes.append(self.__separate_line(self.__pipe(start_index, self.width, *checkin_hours), '\n'))
        pipes.append(self.__separate_line(self.__pipe(start_index, self.width, *dayoff), '\n'))
        pipes.append(self.__separate_line(self.__pipe(start_index, self.width, *done), '\n'))
        return pipes

    def __decorate_today(self, month, week_line):
        if month.today:
            day = date.today().day
            index = week_line.find(' ' + str(day) + ' ')
            if index > 0:
                week_line = list(week_line)
                week_line[index - 1] = '['
                r_offset = 3 if day < 10 else 4
                week_line[index + r_offset] = ']'
                week_line = ''.join(week_line)
        return week_line

    def __print_holiday(self, schedule):
        holidays = schedule.month.holidays
        if holidays and len(holidays):
            for holiday in holidays:
                print('{year}.{month}.{day}  {name}'
                      .format(year=holiday.year, month=holiday.month, day=holiday.day, name=holiday.name))

    def __print_today(self, schedule):
        day = schedule.month.today
        day_name = date.today().strftime('%A')
        if day:
            holiday = '** {} **'.format(day.holiday.name) if day.holiday else ''
            checkin_or_dayoff = '\t Checkin: {}'.format(day.checkin_manhour) if not day.is_dayoff else '\t Day off'
            print('Today:', str(day.date), day_name, holiday, '\t Schedule(OT):', day.scheduled_work_hours,
                  '({})'.format(day.overtime), checkin_or_dayoff)
        else:
            print('today:', date.today(), day_name)

    def __print_manhour_expect(self, schedule):
        workdays = len(schedule.month.days) - len(schedule.dayoff_list)
        salary = schedule.job.required_manhour * schedule.job.hourly_pay
        print('Expecting:', 'Manhour/Workdays = {0}/{1}'.format(schedule.job.required_manhour, workdays),
              '\t Salary = {}'.format(salary))

    def __print_manhour_fornow(self, schedule):
        print('For now:  ', 'Checkin manhour = {}'.format(schedule.checkin_manhour),
              '\t Remaining manhour = {}'.format(schedule.manhour_remain),
              '\t Overtime = {}'.format(schedule.overhours),
              '\t Salary = {}'.format(schedule.checkin_manhour * schedule.job.hourly_pay))

    def __print_manhour_absence(self, schedule):
        if schedule.manhour_absence > 0:
            print('These manhour can not be scheduled on this month:', schedule.manhour_absence)

    def draw(self, schedule: Schedule):
        cal = str(calendar.month(schedule.month.index['year'], schedule.month.index['month'], self.width))
        cal_lines = [' ' + w for w in cal.splitlines() if w != '']

        title = cal_lines.pop(0)
        day_of_week = cal_lines.pop(0)
        cal_weeks = cal_lines

        print('', title, self.hr_line, day_of_week, self.__separate_line(self.hr_line), sep='\n')
        for i in range(len(cal_weeks)):
            print(self.__separate_line(self.__decorate_today(schedule.month, cal_weeks[i])))
            print(*self.__packup_week_schedule(schedule.month.weeks[i]), sep='', end='')
            print(self.__separate_line(self.hr_line))
        print('(Sched = Schedule, OT = Overtime)')
        self.__print_holiday(schedule)
        print('')
        self.__print_today(schedule)
        self.__print_manhour_expect(schedule)
        self.__print_manhour_fornow(schedule)
        self.__print_manhour_absence(schedule)
