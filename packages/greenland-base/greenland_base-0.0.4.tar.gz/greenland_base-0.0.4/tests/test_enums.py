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

from greenland.base.enums import Enum


def test_base_enums():

    # Defining a Weekday Enum

    class Weekday(Enum):
        pass

    # Members are defined by deriving from that class

    class MONDAY(Weekday):
        pass

    class TUESDAY(Weekday):
        pass

    class WEDNESDAY(Weekday):
        pass

    class THURSDAY(Weekday):
        pass

    class FRIDAY(Weekday):
        pass

    class SATURDAY(Weekday):
        pass

    class SUNDAY(Weekday):
        pass

    class LOKIDAY(Weekday):
        set_ord = 13

    class DOOMSDAY(Weekday):
        pass

    # Attributes

    assert WEDNESDAY.ord == 2
    assert len(Weekday) == 9
    assert str(WEDNESDAY) == "WEDNESDAY"
    assert repr(WEDNESDAY) == "WEDNESDAY"
    assert TUESDAY.enum_type == Weekday

    # Weekday.members is an iterator, so you cannot interfere with
    # internal data structures. If you need a list or a tuple you will
    # have to convert.

    assert list(Weekday.members) == [
        MONDAY,
        TUESDAY,
        WEDNESDAY,
        THURSDAY,
        FRIDAY,
        SATURDAY,
        SUNDAY,
        LOKIDAY,
        DOOMSDAY
    ]

    # Ordering

    assert TUESDAY < FRIDAY
    assert FRIDAY == FRIDAY
    assert TUESDAY > MONDAY

    # Membership tests

    assert TUESDAY in Weekday

    class STRAY:
        pass

    assert STRAY not in Weekday

    # Internal procedure used to differentiate between an Enum type
    # and its members.

    assert not MONDAY._is_enum_type
    assert MONDAY._is_enum_member

    assert Weekday._is_enum_type
    assert not Weekday._is_enum_member

    # converting from and to strings

    assert str(TUESDAY) == 'TUESDAY'
    assert TUESDAY.name == 'TUESDAY'
    assert Weekday('TUESDAY') == TUESDAY

    # converting from and to ordinals

    assert int(THURSDAY) == 3
    assert THURSDAY.ord == 3
    assert Weekday(3) == THURSDAY

    # Explicitely declared ordinal

    assert LOKIDAY.ord == 13
    assert DOOMSDAY.ord == 14

    # TODO: Add tests for errors and asserts
