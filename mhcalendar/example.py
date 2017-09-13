#!/usr/bin/env python3
# @Time    : 17-9-2 01:39
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : example.py

"""
Example to run the program.
"""

import mhcalendar.io as io
import mhcalendar.time_elements as mh
from mhcalendar.job import Job

month = mh.Month(2017, 9)

job = Job(required_manhour=120, daily_work_hours=7.5, hourly_pay=2000, max_daily_overhours=2)
schedule = mh.Schedule(job, month)
schedule.schedule(0.5)

mhc = io.MHCalendarDrawer(width=14)
mhc.draw(schedule)

month.next_day.checkin(7.5)
month.next_day.checkin()
month.next_day.checkin()
month.next_day.checkin()

schedule.adjust(day_off=[6, 12, -9, -17])
schedule.schedule(0.5)

mhc.draw(schedule)
