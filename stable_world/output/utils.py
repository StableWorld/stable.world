from datetime import datetime
from dateutil.tz import tzutc


def prettydate(d, now=None):
    """
    format human readable timedelta from now
    """
    if now is None:
        now = datetime.now(tzutc())
    diff = now - d

    s = diff.seconds
    # if diff.days > 7 or diff.days < 0:
    #     return d.strftime('%d %b %y')
    if diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s // 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s // 3600)
