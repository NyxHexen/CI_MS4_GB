from datetime import datetime, time, timedelta


def default_start_datetime():
    return datetime.combine(datetime.now().date(), time(hour=0, minute=1))

def default_end_datetime():
    return datetime.combine(datetime.now().date(), time(hour=0, minute=1)) + timedelta(days=1)