#!/usr/bin/env python3
# @Time    : 17-9-2 01:53
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : job.py

"""
Process information of the job.
"""


class Job:
    def __init__(self, required_manhour=0, daily_work_hours=0, hourly_pay=0, max_daily_overhours=0):
        """
        Define your job's condition.

        :param required_manhour: monthly manhour required by company
        :param daily_work_hours: daily work hours required by company
        :param hourly_pay: hourly pay offers by company
        :param max_daily_overhours: how many hours you can work overtime per day
        """
        self.required_manhour = required_manhour
        self.daily_work_hours = daily_work_hours
        self.hourly_pay = hourly_pay
        self.max_daily_overhours = max_daily_overhours
