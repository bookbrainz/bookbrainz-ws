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

from bbschema import Publication, PublicationType
from entity_testing import EntityTestCases
from sample_data_helper_functions import *
from check_helper_functions import *
import json


class TestPublication(EntityTestCases):
    def specific_setup(self):
        pass

    def set_specific_names(self):
        self.specific_names['entity_class'] = Publication
        self.specific_names['type_name'] = u'Publication'
        self.specific_names['ws_name'] = 'publication'
        self.specific_names['entity_type_id'] = 'publication_type_id'
        self.specific_names['entity_type'] = 'publication_type'
        self.specific_names['entity_type_class'] = PublicationType

    def prepare_put_data(self, instance):
        data = {}

        maybe_add(data, u'publication_type',
                  {u'publication_type_id': random_publication_type_id()})
        mutual_put_data_prepare(data, instance)

        return data

    def prepare_post_data(self):
        data = {}

        maybe_add(data, u'publication_type',
                  {u'publication_type_id': random_publication_type_id()})
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
        check_uri_suffix(
            self,
            response.json['editions_uri'],
            '/{}/{}/{}'.format(
                'publication',
                instance.entity_gid,
                'editions'
            )
        )

    def post_data_check_specific(self, json_data, data):
        pass
