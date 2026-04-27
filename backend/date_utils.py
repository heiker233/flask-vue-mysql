from datetime import datetime, timedelta


DATE_ONLY_FORMAT = '%Y-%m-%d'


def parse_date_start(date_str):
    return datetime.strptime(date_str, DATE_ONLY_FORMAT)


def parse_date_end_exclusive(date_str):
    return parse_date_start(date_str) + timedelta(days=1)
