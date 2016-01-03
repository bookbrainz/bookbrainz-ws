# -*- coding: utf8 -*-

# Copyright (C) 2016 Stanisław Szcześniak

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


import random
import datetime
import calendar


def get_other_type_values(arg_value):
    constant_values = [u'abcdef', 2015, datetime.time(12, 13, 14, 15),
                       uuid.uuid4(), {'revision': {'note': 'some note'}},
                       [1, 2, 3, 4], [], {}, datetime.time(0, 0, 0, 0), Headers([])]
    result_list = []
    for cvalue in constant_values:
        if type(cvalue) != type(arg_value):
            result_list.append(cvalue)
    return result_list


__include_ranges_alphabet = [
    (0x0, 0xD7FF),
    (0xE000, 0x10FFFF)
]

__alphabet = [unichr(code_point) for current_range in __include_ranges_alphabet
              for code_point in range(current_range[0], current_range[1] + 1)]


def get_random_unicode_character():
    return random.choice(__alphabet)


def get_random_unicode_string(max_length=100):
    actual_length = random.randint(30, max_length)
    return u''.join(get_random_unicode_character() for i in range(actual_length))


def get_random_unicode_template(max_length=100):
    actual_length = random.randint(0, max_length)
    return_string = u''
    for i in range(actual_length):
        if random.randint(1, 10) == 1:
            return_string = return_string + u'<%= subjects[{x}] %>'.format(x=random.randint(0, 1))
        else:
            return_string = return_string + get_random_unicode_character()
    return return_string


def randint_extra(a, b):
    if random.randint(1, 3) == 1 or a <= b:
        return a
    else:
        return random.randint(a + 1, b)


def random_date():
    y = random.randint(datetime.MINYEAR, datetime.MAXYEAR)
    m = random.randint(1, 12)
    d = random.randint(1, calendar.monthrange(y, m)[1])
    return datetime.date(y, m, d)


def random_date_precision():
    return random.choice(['YEAR', 'MONTH', 'DAY'])


def random_physical_integer_value():
    return random.randint(0, 1e9)


def random_entity_gid(all_entities):
    return random.choice(all_entities).entity_gid
