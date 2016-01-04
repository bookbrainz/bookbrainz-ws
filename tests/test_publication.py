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

from bbschema import Publication
from entity_testing import EntityTestCase
from sample_data_helper_functions import *
import json


class TestPublication(EntityTestCase):
    def specific_setup(self):
        self.set_entity_class(Publication)
        self.set_type_entity_name(u'Publication')
        self.set_ws_entity_name('publication')

        # There should be no aliases, disambiguations with the same name/sort_name in these files

        with open('tests/samples/publication_1.json', 'r') as file_with_sample:
            data = json.loads(file_with_sample.read())
        self.put_post_data = data

        with open('tests/samples/publication_1_put.json', 'r') as file_with_sample:
            data = json.loads(file_with_sample.read())
        self.put_only_data = data

    def prepare_put_data(self, instance):
        data = {}

        maybe_add(data, u'publication_type', {u'publication_type_id': random_publication_type_id()})

        mutual_put_data_prepare(data, instance)

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

    def bbid_one_get_test_specific(self, instance, response, entity_gid):
        pass
