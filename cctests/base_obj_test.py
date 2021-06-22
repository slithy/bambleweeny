import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

import pytest

from cogscc.base_obj import BaseObj


class A(BaseObj):
    def __init__(self, int0, list0, dict0):
        super().__init__()
        self.int0 = int0
        self.list0 = list0
        self.dict0 = dict0


class B(A):
    def __init__(self, int0, list0, dict0, int1, list1, dict1, A0):
        super().__init__(int0, list0, dict0)
        self.int1 = int1
        self.list1 = list1
        self.dict1 = dict1
        self.A0 = A0


def test_base_obj_eq():
    a0 = A(3, [1, 2], {"z": 1, "z": 2})
    a1 = A(3, [1, 2], {"z": 1, "z": 2})
    assert a0 == a1
    a1.int0 = 2
    assert a0 != a1
    b0 = B(3, [1, 2], {"z": 1, "q": 2}, 4, [2, 3], {"z": 4, "y": 5}, a0)
    assert b0 != a1
    assert a1 != b0
    a1.int0 = 3
    b1 = B(3, [1, 2], {"z": 1, "q": 2}, 4, [2, 3], {"z": 4, "y": 5}, a1)
    assert b0 == b1
    b1.list0[0] = 10
    assert b0 != b1
    b1.list0[0] = 1
    assert b0 == b1
    b1.dict1["y"] = 1
    assert b0 != b1
    b1.dict1["y"] = 5
    assert b0 == b1
    a1.list0[1] = 10
    assert b0 != b1


def test_to_and_from_dict():
    a0 = A(3, [1, 2], {"z": 1, "z": 2})
    a1 = A.__from_dict__(a0.__to_json__())
    assert a1 == a0
    b0 = B(3, [1, 2], {"z": 1, "q": 2}, 4, [2, 3], {"z": 4, "y": 5}, a0)
    b1 = B.__from_dict__(b0.__to_json__())
    assert b0 == b1
    with pytest.raises(TypeError):
        a2 = A.__from_dict__(b0.__to_json__())
