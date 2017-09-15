#!/usr/bin/env python3
# @Time    : 17-9-9 18:27
# @Author  : Wavky Huang
# @Contact : master@wavky.com
# @File    : setup.py.py

"""

"""
from setuptools import setup, find_packages

from meta import *

setup(
    name=PROJECT_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description='Calendar to manage your man-hour.',
    long_description=open('README.rst').read(),
    url='https://github.com/wavky/ManHourCalendar',
    license='MIT',
    keywords=['man-hour', 'manhour', 'man hour', 'calendar', 'schedule'],
    python_requires='>=3',
    packages=find_packages(),
    py_modules=['meta'],
    install_requires=['docopt>=0.6.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Environment :: Console'
    ],
    entry_points={
        'console_scripts': [
            'mhcalendar = scripts.mhcalendar:main'
        ]
    }
)
