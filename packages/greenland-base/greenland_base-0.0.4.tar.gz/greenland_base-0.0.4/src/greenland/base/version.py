#
# version.py -- Product / package and version information
# Copyright (C) 2024  M E Leypold
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
#

import subprocess
import os
from typing import Union

version: Union[str, None]  = None
version_tuple: Union[
    tuple[int, int, int, Union[str, None], Union[str, None]], None
] = None

#
# version_tuple = (MAJOR, MINOR, MICRO, LOCAL, COMMIT)
# e.g. (0, 0, 2, 'dev0', 'g9bb28fd.d20240825')


def __editable_install__():
    return __file__[:-(len(__name__) + 3)][-5:] == "/src/"


if not __editable_install__():
    try:
        from .__version__ import version as _version
        from .__version__ import version_tuple as _version_tuple
        version = _version

        if len(_version_tuple) >= 4:
            _local = _version_tuple[3]
        else:
            _local = None

        if len(_version_tuple) >= 5:
            _commit = _version_tuple[3]
        else:
            _commit = None

        version_tuple = (
            *_version_tuple[0:3], _local, _commit
        )

    except ModuleNotFoundError:
        pass

if version is None:
    from packaging.version import parse

    # TODO: Must CD to __file__

    r = subprocess.run(
        ["hatch", "version"], encoding = 'utf-8',
        cwd = os.path.dirname(__file__),
        capture_output = True, check = True
    )
    version = r.stdout.strip()
    _parsed  = parse(version)
    version_tuple = (
        _parsed.major,
        _parsed.minor,
        _parsed.micro,
        _parsed.local if _parsed.local else "",
        None
    )

product = "-".join(__name__.split('.')[:-1])
program = None


def set_program(name):
    global program
    program = os.path.basename(name)
    return program
