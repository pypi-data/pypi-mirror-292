# test_enums - Testing greenland.base.enums
# Copyright (C) <year>  <name of author>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Union, Type
from functools import total_ordering

# Compatibility restriction: Need python version > 3.8, since in 3.8
# functools.totalordering does not work as expecte for meta classes.
# Currently the approach is not to just not support 3.8. 3.8 will
# reach end of support in 2 months as of writing this, so this will
# probably stay (we could implement and mix in a TotalOrderingViaLt
# class, but it's not worth the bother for a EOL Python
# version. Somebody would have to pay me real money for that.


@total_ordering
class EnumMeta(type):

    def __init__(cls, name, bases, environment):
        super().__init__(name, bases, environment)

        base = bases[0]
        if hasattr(base, '_members') and base._members is not None:
            cls._enum = base

    @property
    def ord(cls):
        return cls._ord

    @property
    def name(cls):
        return cls.__name__

    def __len__(cls):
        return len(cls._members)

    def __repr__(cls):
        if cls._is_enum_member:
            return cls.__name__
        else:
            return super().__repr__()

    def __str__(cls):
        if cls._is_enum_member:
            return cls.__name__
        else:
            return super().__str__()

    def __int__(cls):
        assert cls._is_enum_member
        return cls._ord

    @property
    def members(cls):
        for member in cls._members:
            yield member

    def __eq__(cls, other):
        return cls is other

    def __lt__(cls, other):
        assert cls.__class__ == other.__class__
        return cls._ord < other._ord

    def __contains__(cls, member):
        try:
            return member._enum is cls
        except AttributeError:
            return False

    @property
    def enum_type(cls):
        assert cls._ord is not None
        return cls._enum

    @property
    def _is_enum_member(cls):
        return cls._ord is not None

    @property
    def _is_enum_type(cls):
        return cls._ord is None and cls._members is not None

    def __call__(cls, name_or_ord):
        assert cls._is_enum_type
        if isinstance(name_or_ord, str):
            name = name_or_ord
            if name not in cls._members_by_name:
                raise TypeError(
                    f"{name!r} is not the name of a member of {cls}"
                )
            return cls._members_by_name[name]
        else:
            assert isinstance(name_or_ord, int)
            ord = name_or_ord
            if ord not in cls._members_by_ord:
                raise TypeError(f"no member of {cls} with ordinal {ord!r}")
            return cls._members_by_ord[ord]


class Enum(object, metaclass=EnumMeta):

    _members: Union[None, list[Type['Enum']]] = None
    _members_by_name: Union[None, dict[str, Type['Enum']]] = None
    _members_by_ord: Union[None, dict[int, Type['Enum']]] = None

    _ord: Union[None, int] = None

    def __init_subclass__(cls, *pargs, **kwargs):
        if cls._members is None:
            cls._members = []
            cls._members_by_name = {}
            cls._members_by_ord = {}
        else:
            try:
                cls._ord = cls.set_ord
                del cls.set_ord
            except (AttributeError, KeyError):
                cls._ord = \
                    max(cls._members_by_ord.keys()) + 1 \
                    if len(cls._members) else 0
            cls._members.append(cls)
            assert cls.__name__ not in cls._members_by_name, \
                "Duplicate member name"
            cls._members_by_name[cls.__name__] = cls
            assert cls._ord not in cls._members_by_ord, \
                "Duplicate member ordinal"
            cls._members_by_ord[cls._ord] = cls

# TODO: Make members into a map (for parsing strings) and also check
# for duplicate member names.

# TODO: Instantiate from strings (only for enum types)

# TODO: Try to lock down methods that do not make sense for
# members. Here we probably need to intercept __new__ or __prepare__.

# TODO: allow ord (or so) to turn up in member definition and override
# _ord this way. enumeration of subsequent items must continue with
# this value.
