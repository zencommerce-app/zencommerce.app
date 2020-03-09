"""
Utilities funtions
"""

from datetime import datetime


def _normalize_bool(val):
    """
    2019 Nov 09: For some reason ETSY API returns string 'false' / 'true' for
    'is_supply' property.
    https://www.etsy.com/developers/documentation/reference/listing
    """

    if type(val) == str:
        return val == 'true'
    elif type(val) == bool:
        return val
    # TODO: check for other options
    return False


def _jobs_log(item, msg):
    """
    Appends msg to object's 'jobs_log' field.
    """

    ts = datetime.now().isoformat(' ', 'seconds')

    if hasattr(item, 'jobs_log'):
        item.jobs_log = '{} {}\n'.format(ts, msg) + item.jobs_log
        item.save()


def _to_int(val):
    try:
        return int(val)
    except:
        return None


def _to_str(val):
    return str(val)


def _to_str_bool(val):
    try:
        if int(val) == 1:
            return 'true'
        else:
            return 'false'
    except:
        return 'false'
