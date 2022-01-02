# import for handling date
import datetime


def date_to_str(date):
    str_format = '%Y-%m-%d'
    return datetime.datetime.strftime(date, str_format)


def str_to_date(date):
    str_format = '%Y-%m-%d'
    return datetime.datetime.strptime(date, str_format)


def day_pass(date):
    return date + datetime.timedelta(days=1)


def is_month_start(date):
    return date.day == 1
