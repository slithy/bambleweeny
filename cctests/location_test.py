import sys, os

rootpath = os.path.realpath(os.path.dirname(__file__) + "/..")
if rootpath not in sys.path:
    sys.path.append(rootpath)

import pytest
from cogscc.models.errors import InvalidArgument
from cogscc.world.location import GHLocation


def test_eq():
    l1 = GHLocation()
    l2 = GHLocation()
    assert l1 == l2
    l3 = GHLocation("new town")
    assert l1 != l3
    l4 = GHLocation("new town")
    assert l3 == l4


def test_set_terrain():
    l1 = GHLocation()
    l1.set_terrain("hill")
    assert l1.terrain == "hill"
    with pytest.raises(InvalidArgument):
        l1.set_terrain("not a terrain")
