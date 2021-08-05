import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

from cogscc.funcs import utils


def test_d2std_time():
    t = [0, 12, 0]
    assert t == utils.d2std_time(t[0] + t[1] / 24 + t[2] / (60 * 24))
    t = [0, 0, 0]
    assert t == utils.d2std_time(t[0] + t[1] / 24 + t[2] / (60 * 24))
    t = [34, 0, 0]
    assert t == utils.d2std_time(t[0] + t[1] / 24 + t[2] / (60 * 24))
    t = [0, 0, 55]
    assert t == utils.d2std_time(t[0] + t[1] / 24 + t[2] / (60 * 24))
    t = [0, 0, 60]
    assert [0, 1, 0] == utils.d2std_time(t[0] + t[1] / 24 + t[2] / (60 * 24))

def test_split_long_message():
    s = "a\nb\nc\nd\ne\nf\ng\nh\ni\nl\na\na\na\navava\na\na\na\navava\na\nava\na\nava\nav\n\nvsvsssvsvs\n\nvs\nv\nl" \
        "\nl\nl\nl\nl\n\nl\nl\nl\nl\nl\nl\na\nb"
    print(s)
    print("-----")
    out = utils.split_long_message(s)
    print()
    for i in out:
        print(i.count("\n"))
