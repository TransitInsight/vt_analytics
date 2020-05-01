from datetime import datetime
from datetime import timedelta


def NormalizeDate(start_date, end_date):
    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    return start_date, end_date
