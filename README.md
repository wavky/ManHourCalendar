Man Hour Calendar
===

A simple monthly calendar for checking and schedule your working man-hours. （Mainly for Japan)

[中文版文档](https://github.com/wavky/ManHourCalendar/blob/master/README.zh.md)

This is a CLI tool, just as my first python project, created to deal with my monthly man-hour calculation.


## Usage
The simply way to use it like this flow:
```sh
# Initialize your Job file first.
# It will also update the Japanese holidays schedule at the first time.
$ python3 mhcalendar.py -J ...

# Check out the man-hour schedule of current month.
$ python3 mhcalendar.py

# Check in your man-hour of first day.
# Ensure that you will check in everyday.
$ python3 mhcalendar.py -c 8

# Check out your schedule again to confirm your next day's work hours.
$ python3 mhcalendar.py


# Schedule your day off or on duty days anytime before it comes.
# For example, make date of 9, 10 and 11 as dayoff, and go to work at 13th.
$ python3 mhcalendar.py --dayoff -- 9 10 11 -13

# Remember to Update your schedule by calling this
$ python3 mhcalendar.py
```

For more information you can check it out by command:
```sh
$ mhcalendar -h
```

Also you can run it by your python script, refer to this file:
[Example.py](https://github.com/wavky/ManHourCalendar/blob/master/mhcalendar/example.py)

## Install
This program is written in python3, you need to install the python3 and pip3 before this installation.
```sh
pip3 install ManHourCalendar
```

## About data
For simple, we haven't use database this time, all data is only cache in this folder as files:
```sh
~/.mhcalendar/
# or your user dir in Windows such as
C:\Users\username\.mhcalendar\
```

And holidays schedule is fetched from the site below:
http://calendar-service.net/

ご提供ありがとうございます！