#!/usr/bin/env python3
# @Time    : 17-9-10 14:46
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : log.py

"""
Log with switch by VERBOSE
"""
VERBOSE = False


def log(*values, sep=' ', end: str = '\n'):
    if VERBOSE:
        print(*values, sep=sep, end=end)
