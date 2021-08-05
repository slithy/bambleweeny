import math

from cogscc.models.errors import *

def smart_find(d, key):
    if key in d:
        return d[key]
    l = [v for k, v in d.items() if key in k]
    if len(l) == 1:
        return l[0]

    if key != key.lower():
        return smart_find(d, key.lower())

    if len(l) == 0:
        raise ItemNotFound(f"No matches for: {key}")
    elif len(l) > 1:
        raise AmbiguousMatch(f"Too many matches for: {key}")

def F2C(T):
    return int(10 * ((T - 32) * 5 / 9)) / 10

def h2d(h):
    return h/24

def m2d(m):
    return m/(60*24)

def d2std_time(d):
    h = (d-int(d))*24
    m = (h-int(h))*60
    return [int(d),int(h),int(m)]

def feet2m(f):
    return 0.3048*f

def m2feet(m):
    return m/0.3048


def split_long_message(s):
    s = s.split("\n")
    out = []
    print(len(s))
    for i in range(math.ceil(len(s)/20)):
        out.append("\n".join(s[i*20:(i+1)*20]))
    return out




