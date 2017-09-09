#!/usr/bin/env python3
# @Time    : 17-9-2 01:39
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : example.py

"""
Example to run the program.
"""

from datetime import date

import src.io as io
import src.time_elements as mh
from src.job import Job

date = date.today()
month = mh.Month(date.year, date.month)
month.initialize_days()

job = Job(required_manhour=170, daily_work_hours=7.5, hourly_pay=2000, max_daily_overhours=2)
schedule = mh.Schedule(job, month)
schedule.schedule()

mhc = io.MHCalendarDrawer(width=14)
mhc.draw(schedule)

month.next_day.checkin(7.5)
month.next_day.checkin()
month.next_day.checkin()
month.next_day.checkin()
schedule.adjust(day_off=[6, 12, -9, -17])
schedule.schedule()
mhc.draw(schedule)
