#!/usr/bin/env python3
# @Time    : 17-9-9 18:34
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : mhcalendar.py

"""Calendar to manage your man-hour.

Usage:
    mhcalendar (-h | --help)
    mhcalendar (-V | --version)
    mhcalendar (-J | --Job) <required_manhour> <daily_work_hours> <hourly_pay> <max_daily_overhours>
    mhcalendar (-j | --job)
    mhcalendar (-M | --Month) <year> <month>
    mhcalendar (-m | --month)
    mhcalendar [-v | --verbose] [-C | --calendar] [--pre <precision>]
    mhcalendar (-c | --checkin) [<hours>]
    mhcalendar (-p | --pointer)
    mhcalendar --dayoff [--] [<date> ...]


Options:
    -h, --help        Show this screen.
    -V, --version     Show version.
    -J, --Job         Create or Update Job's file.
    -j, --job         Show your Job's file.
    -M, --Month       Create or Update Month data, default to current month if unset.
    -m, --month       Show the month which is processing.
    -v, --verbose     Show verbose message, it's about schedule processing now.
    -C, --calendar    Update and Show the calendar with man-hour schedule under specific precision.
    --pre             Specify a minimum time unit to schedule the man-hour. Default to 1(hour).
    -c, --checkin     Check in your man-hours into the date which is pointing to.
    -p, --pointer     Show the date which is pointing to.
                      It will shift to next day after you check in the man-hour.
    --dayoff          Schedule the dates to day off or reverse.


Parameter:
    Job
        required_manhour      Monthly manhour required by company.
        daily_work_hours      Daily work hours required by company.
        hourly_pay            Hourly pay offers by company.
        max_daily_overhours   How many hours you can work overtime per day, while minus means unlimited.

    checkin
        hours                 Hours to check in the date which is pointing to.
                              See --pointer in Options.
                              Default to the scheduled hours of that date if no specify.

    dayoff
        date...               Dates which is planing to take a day off, while minus means
                              that day switches to on duty.
                              You can only set dayoff the date which hasn't checkin.
                              Default to the date which is pointing to if no specify.
                              See --pointer in Options.
                              eg. --dayoff -- -9 -13 23 24


Simple Workflow:
    $ python3 mhcalendar.py -J ...      Create your Job file first.
                                        It will also update the holidays schedule at the first time.
    $ python3 mhcalendar.py             Check out the man-hour schedule of current month.
    $ python3 mhcalendar.py -c 8        Check in your man-hour of first day.
    $ python3 mhcalendar.py             Check out your schedule again to confirm your next day's work hours.

    $ python3 mhcalendar.py --dayoff -- 9 10 11 -13
                                        Schedule your day off or on duty days anytime before it comes.


"""
from docopt import docopt

import meta
import mhcalendar.log as log
import mhcalendar.time_elements as te
from mhcalendar import io
from mhcalendar.job import Job


def main():
    arguments = docopt(__doc__, version=meta.VERSION)
    io.prepare()
    log.VERBOSE = arguments['--verbose']
    if arguments['--Job']:
        job = Job(float(arguments['<required_manhour>']), float(arguments['<daily_work_hours>']),
                  float(arguments['<hourly_pay>']), float(arguments['<max_daily_overhours>']))
        schedule = io.Cache.restore_schedule()
        schedule.job = job
        io.Cache.cache_schedule(schedule)
        return
    if arguments['--job']:
        schedule = io.Cache.restore_schedule()
        check_schedule(schedule)
        print(schedule.job)
        return
    if arguments['--Month']:
        schedule = io.Cache.restore_schedule()
        month = te.Month(int(arguments['<year>']), int(arguments['<month>']))
        schedule.month = month
        io.Cache.cache_schedule(schedule)
        return
    if arguments['--month']:
        schedule = io.Cache.restore_schedule()
        print('Month: ', schedule.month.index['year'], '.', schedule.month.index['month'], sep='')
        return
    if arguments['--checkin']:
        schedule = io.Cache.restore_schedule()
        check_schedule(schedule)
        manhour = arguments['<hours>']
        day_to_checkin = schedule.month.next_day
        if not day_to_checkin:
            raise Exception()
        if manhour:
            day_to_checkin.checkin(float(manhour))
        else:
            day_to_checkin.checkin()
        io.Cache.cache_schedule(schedule)
        print("Date: {0}.{1}.{2} {3} \t Check in hours: {4}".format(day_to_checkin.date.year, day_to_checkin.date.month,
                                                                    day_to_checkin.date.day,
                                                                    day_to_checkin.date.strftime('%A'),
                                                                    day_to_checkin.checkin_manhour))
        return
    if arguments['--pointer']:
        schedule = io.Cache.restore_schedule()
        check_schedule(schedule)
        print(schedule.month.next_day)
        return
    if arguments['--dayoff']:
        schedule = io.Cache.restore_schedule()
        check_schedule(schedule)
        dates = arguments['<date>']

        if not dates or len(dates) == 0:
            dates = [-schedule.month.next_day.date.day]

        schedule.adjust(day_off=dates)
        io.Cache.cache_schedule(schedule)
        return

    # default to show calendar
    schedule_precision = arguments['<precision>'] or 1
    schedule = io.Cache.restore_schedule()
    check_schedule(schedule)

    schedule.schedule(schedule_precision)
    io.MHCalendarDrawer().draw(schedule)
    io.Cache.cache_schedule(schedule)


def check_schedule(schedule):
    if not schedule:
        raise Exception("Initialize error. Try again.")
    if not schedule.job:
        raise Exception("You haven't create your Job file yet.")
    if not schedule.month.next_day:
        raise Exception("This month's schedule is completed already.\nUpdate your Month data for next schedule.")


if __name__ == '__main__':
    main()
