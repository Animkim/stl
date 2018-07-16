from django.conf import settings


def strip_int(s):
    def isdigit(d):
        if d in '0123456789.':
            return d
        return ''

    s = s.replace(' ', ' ')
    if s.count(',') == 1 and settings.ACTIVE_LANG == 'ru':
        s = s.replace(',', '.')
    else:
        s = s.replace(',', '')
    return ''.join([isdigit(d) for d in s])


def parse_int(s):
    if isinstance(s, (int, float)):
        return s
    if not s:
        return None
    s = s.strip()
    s = strip_int(s)

    try:
        return min(2**31 - 1, int(s))
    except ValueError:
        pass
    try:
        return min(2**31 - 1, int(float(s)))
    except ValueError:
        pass
