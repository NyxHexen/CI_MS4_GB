from datetime import datetime, time


def default_datetime():
    return datetime.combine(datetime.now().date(), time(hour=0, minute=1))