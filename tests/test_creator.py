# -*- coding: utf8 -*-

# Copyright (C) 2015, 2016 Stanisław Szcześniak

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

from bbschema import Creator
from entity_testing import EntityTestCase
from sample_data_helper_functions import *
import json


class TestCreator(EntityTestCase):
    def specific_setup(self):
        self.set_entity_class(Creator)
        self.set_type_entity_name(u'Creator')
        self.set_ws_entity_name('creator')

    def prepare_put_data(self, instance):
        data = {}

        self.prepare_put_post_not_specific_data(data)
        mutual_put_data_prepare(data, instance)

        return data

    def prepare_post_data(self):
        data = {}

        self.prepare_put_post_not_specific_data(data)
        mutual_post_data_prepare(data)

        return data

    def prepare_put_post_not_specific_data(self, data):
        r_begin_date, r_begin_date_precision = string_random_date()
        is_added = maybe_add(data, u'begin_date', r_begin_date)
        if is_added:
            maybe_add(data, u'begin_date_precision',
                      r_begin_date_precision, maybe=False)

        r_end_date, r_end_date_precision = string_random_date()
        is_added = maybe_add(data, u'end_date', r_end_date)
        if is_added:
            maybe_add(data, u'end_date_precision',
                      r_end_date_precision, maybe=False)

        maybe_add(data, u'ended', random_boolean())

        maybe_add(data, u'gender', {u'gender_id': random_gender_id()})

        maybe_add(data, u'creator_type',
                  {u'creator_type_id': random_creator_type_id()})

    def test_get_bbid(self):
        self.bbid_get_tests()

    def test_get_list(self):
        self.list_get_tests()

    def test_post(self):
        self.post_tests()

    def test_put(self):
        self.put_tests()

    def test_delete(self):
        self.delete_tests()

    def bbid_one_get_test_specific_checking(self, instance, response, gid):
        pass
