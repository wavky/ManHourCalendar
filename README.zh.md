Man Hour Calendar
===

用于计算、分配工时的一个月历（主要为日本工作的小伙伴们提供服务 :P）

该程序是一款基于命令行的简单脚本程序，使用python3编写，作为个人第一款python程序，当前版本仅提供有限而必须的功能，主要为派遣工作中月标准时的概念进行工作量计算和分配，并提供每天打卡、工时录入进度更新功能。

本月历同时提供了当月日本法定节假日数据，该数据从以下网站上获取：
http://calendar-service.net/

## Usage
简单通用的使用方式如下
```sh
# 首先需要创建您的工作资料，需要录入以下数据：
# required_manhour		合同规定的月标准时
# daily_work_hours		现场或公司规定的每天正常工作时间
# hourly_pay			时薪，该数据仅用于统计
# max_daily_overhours	可接受的每天加班时间上限（不包括正常工作时间）
# 首次运行时会从上述网站中获取全年节假日数据
$ python3 mhcalendar.py -J ...

# 检查您本月的工时编排表
$ python3 mhcalendar.py

# 录入您当天的实际工时（请确保每天进行录入，包括节假日）
$ python3 mhcalendar.py -c 8
# 节假日没有工时安排时，或实际工时与计划工时一致时，可简单录入
$ python3 mhcalendar.py -c

# 再次检查您的月历表，查看下一天的工时数
# 该过程会依据您刚才录入的实际工时数，再次计算分配日均工时量
$ python3 mhcalendar.py

----------------------------------------------------

# 当需要更改本月休息、上班日期时，可通过该命令进行指定，但仅限于未录入工时的日子
# 例如，指定9、10、11日为休假，13日上班（假定13日为节假日或周末）
$ python3 mhcalendar.py --dayoff -- 9 10 11 -13

# 指定修改完毕后，刷新显示月历以更新工时编排表
$ python3 mhcalendar.py

# 程序首次运行时会自动初始化为当前月份，需要更新月份时，使用该命令执行
$ python3 mhcalendar.py -M 2017 9

```

通过 -h 参数获取详细帮助文档（英文）
```sh
$ mhcalendar -h
```

下载源码，并以脚本方式运行时，可参考该文件：
[Example.py]()

## Install
该程序使用python3编写，您需要先确定当前使用pip程序对应于phthon3，并使用pip程序进行安装：
```sh
pip3 install ManHourCalendar
```

## About data
出于简（tou）便（lan），当前版本并未使用数据库进行存储，所有录入数据均以文件方式存放在以下位置
```sh
~/.mhcalendar/
# Windows系统目录如下
C:\Users\username\.mhcalendar\
```