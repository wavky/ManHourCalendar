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

# 每列宽度
width = 16
cal = str(calendar.month(2017, 9, width))
weeks = [' ' + w for w in cal.split('\n') if w != '']

for week in weeks:
    print(week)
    mark = '-' * width + '|'
    print('|' + mark * 7)

import src.manhour_calendar as manhour
from datetime import date

date = date.today()
month = manhour.Month(date.year, date.month)
month.initialize_days()
print(month.holidays)
print(month.days)
print(month)
