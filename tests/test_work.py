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

from bbschema import Work, WorkType
from entity_testing import EntityTestCases
from sample_data_helper_functions import *
from check_helper_functions import *


class TestWork(EntityTestCases):
    def specific_setup(self):
        pass

    def set_specific_names(self):
        self.specific_names['entity_class'] = Work
        self.specific_names['type_name'] = u'Work'
        self.specific_names['ws_name'] = 'work'
        self.specific_names['entity_type_id'] = 'work_type_id'
        self.specific_names['entity_type'] = 'work_type'
        self.specific_names['entity_type_class'] = WorkType

    def prepare_put_data(self, instance):
        data = {}

        maybe_add(data, u'work_type', {u'work_type_id': random_work_type_id()})
        maybe_add(data, u'languages', random_put_languages_prepare(instance))
        mutual_put_data_prepare(data, instance)

        return data

    def prepare_post_data(self):
        data = {}

        maybe_add(data, u'work_type', {u'work_type_id': random_work_type_id()})
        maybe_add(data, u'languages', random_post_languages_prepare())
        mutual_post_data_prepare(data)

        return data

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

    def bbid_one_get_tests_specific_check(self, instance, response):
        check_languages_json(
            self,
            response.json['languages'],
            instance.master_revision.entity_data.languages
        )

    def post_data_check_specific(self, json_data, data):
        self.post_check_languages_json(
            json_data,
            data.master_revision.entity_data
        )
