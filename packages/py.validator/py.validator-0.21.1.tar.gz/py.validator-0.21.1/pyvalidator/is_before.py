from .utils.to_date import default_date_string, to_date


def is_before(input, date=default_date_string()):
    comparison = to_date(date)
    original = to_date(input)
    return bool(original and comparison and original < comparison)
