# Copyright (C) 2023,2024 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# pylint: disable=W0622

"""A console program that generates yearly calendar heatmap."""

import argparse
import platform
import sys

__version__ = "0.12.20"


class EnvironmentAction(argparse.Action):
    """Show environment details action."""

    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help=None,
    ):
        """Overwrite class method."""
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        """Overwrite class method."""
        sys_version = sys.version.replace("\n", "")
        print(
            f"heatmap: {__version__}",
            f"python: {sys_version}",
            f"platform: {platform.platform()}",
            sep="\n",
        )
        parser.exit()
