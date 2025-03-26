# -*- coding: utf-8 -*-
"""
Borg design pattern implementation, using inheritance approach
"""

from typing import ClassVar


# noinspection PyArgumentList
class Borg:
    """
    Implementation of the Borg design pattern.

    Have subclasses share their state, rather than their identity
    Easier to work with unittest than with Singleton DP.

    Taken from :
    http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    To use with moderation, since class instances are not limited. Their
    State is simply shared by them.

    """

    _state: ClassVar[dict] = {}

    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._state
        return self
