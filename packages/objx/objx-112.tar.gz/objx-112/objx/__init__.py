# This file is placed in the Public Domain.
# pylint: disable=W0401,W0611,W0622,W0614
# ruff: noqa: F401,F403


"""objects

OBJX contains all the python3 code to program objects in a functional
way. It provides a base Object class that has only dunder methods, all
methods are factored out into functions with the objects as the first
argument. It is called Object Programming (OP), OOP without the
oriented.

OBJX  allows for easy json save//load to/from disk of objects. It
provides a "clean namespace" Object class so the namespace is not
cluttered with method names. This makes storing and reading to/from
json possible.


>>> from objx import Object, dumps, loads
>>> o = Object()
>>> o.a = "b"
>>> print(loads(dumps(o))
{'a': 'b'}


OBJX is Public Domain."""


from . import decoder, encoder, object


from .decoder import *
from .encoder import *
from .object  import *


def __dir__():
    return (
        'Object',
        'construct',
        'dump',
        'dumps',
        'edit',
        'fmt',
        'fqn',
        'hook',
        'ident',
        'items',
        'keys',
        'load',
        'loads',
        'match',
        'read',
        'search',
        'update',
        'values',
        'write'
    )
