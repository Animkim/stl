

def parse_int(s):
    if isinstance(s, (int, float)):
        return s
    if not s:
        return None
    s = s.strip()
    try:
        return min(2**31 - 1, int(s))
    except ValueError:
        pass
    try:
        return min(2**31 - 1, int(float(s)))
    except ValueError:
        pass
