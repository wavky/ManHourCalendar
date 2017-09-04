#!/usr/bin/env python3
# @Time    : 17-9-2 01:39
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : main.py

"""
Example to run the program.
"""
# from src.manhour_calendar import update_holiday_schedule
# holiday = update_holiday_schedule()
# list(map(print,holiday))

import calendar
from datetime import date

import src.manhour_calendar as manhour

date = date.today()
month = manhour.Month(date.year, date.month)
month.initialize_days()

# datelist = list(calendar.Calendar().itermonthdays(2017, 9))
# WeekdayIndex = namedtuple('WeekdayIndex',('week','weekday'))

# def indexof(date: int):
#     index = datelist.index(date)
#     week = index // 7
#     weekday = index % 7
#     return WeekdayIndex(week, weekday)


# print(header)
# for i in range(1, len(month.days) + 1):
#     print(i, ':', indexof(i))

# 每列宽度
width = 12
cal = str(calendar.month(2017, 9, width))
weeks = [' ' + w for w in cal.split('\n') if w != '']

blank = '\n'
header = '-' * (width + 1) * 7 + '-'
seperator = '|' + ('-' * width + '|') * 7

title = weeks.pop(0)
day_of_week = weeks.pop(0)

monthday_matrix = calendar.Calendar().monthdayscalendar(2017, 9)
print(monthday_matrix)


def print_blank(): print('\n', end='')


def firstday_of_week(week):
    """
    :param week: list of date
    :return: first day index of week
    """
    for i in week:
        if i > 0:
            return week.index(i)
    return -1


print_blank()
print()
print(title)
print(header)
print(day_of_week)
print(seperator)

for i in range(len(weeks)):
    print(weeks[i])
    # print_blank()
    start_index = firstday_of_week(monthday_matrix[i]) * (width + 1) + 1
    print(' ' * start_index + 'Required: 14')
    print(seperator)


def pipe(start, width, *texts):
    """
    The real name is Pile In piPE :P

    :param start: offset to start
    :param width: pipe's width
    :param texts: text to fill into a pipe
    :return: a bamboo...
    """
    elements = [' ' * start, ]
    for t in texts:
        lent = len(t)
        if lent < width:
            t += ' ' * (width - lent)
        elements.append(t)
    return ''.join(elements)


print(pipe(1, width + 1, "Requi: 14", "Required: 14", "Rui: 1", "Requi: 14"))
