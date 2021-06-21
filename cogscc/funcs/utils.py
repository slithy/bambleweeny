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

