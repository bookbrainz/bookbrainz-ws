# -*- coding: utf8 -*-

# Copyright (C) 2015, 2016 Ben Ockmore, Stanisław Szcześniak

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
    test.py includes running all the tests in /tests/
    and logging initialization

    To enable the tests run test.py with --logs
"""

import unittest
import tests
import logging
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--logs', help='log level')
args = parser.parse_args()

if args.logs:
    logging.basicConfig(
        format='%(levelname)s:%(message)s',
        level=getattr(logging, args.logs.upper(), None)
    )
else:
    logging.basicConfig(
        format='%(levelname)s:%(message)s',
        level=logging.CRITICAL
    )

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main(tests)
