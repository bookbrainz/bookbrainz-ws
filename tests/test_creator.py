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

from bbschema import Creator, CreatorType
from entity_testing import EntityTests
from sample_data_helper_functions import *
from check_helper_functions import *
import json


class TestCreator(EntityTests):
    def specific_setup(self):
        pass

    def set_specific_names(self):
        self.specific_names['entity_class'] = Creator
        self.specific_names['type_name'] = u'Creator'
        self.specific_names['ws_name'] = 'creator'
        self.specific_names['entity_type_id'] = 'creator_type_id'
        self.specific_names['entity_type'] = 'creator_type'
        self.specific_names['entity_type_class'] = CreatorType

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

    def bbid_one_get_tests_specific_check(self, instance, response):
        check_date_json(
            self,
            response.json['begin_date'],
            response.json['begin_date_precision'],
            instance.master_revision.entity_data.begin_date,
            instance.master_revision.entity_data.begin_date_precision
        )
        check_date_json(
            self,
            response.json['end_date'],
            response.json['end_date_precision'],
            instance.master_revision.entity_data.end_date,
            instance.master_revision.entity_data.end_date_precision
        )

        self.assertEquals(
            response.json['ended'],
            instance.master_revision.entity_data.ended
        )

        check_country_id(
            self,
            response.json,
            instance.master_revision.entity_data.country_id
        )

        check_gender_json(
            self,
            response.json['gender'],
            instance.master_revision.entity_data.gender
        )

    def post_data_check_specific(self, json_data, data):
        data = data.master_revision.entity_data

        if 'begin_date' in json_data:
            self.put_post_check_date_json(
                json_data['begin_date'],
                data.begin_date,
                data.begin_date_precision
            )
        else:
            self.assertIsNone(data.begin_date)
            self.assertIsNone(data.begin_date_precision)

        if 'end_date' in json_data:
            self.put_post_check_date_json(
                json_data['end_date'],
                data.end_date,
                data.end_date_precision
            )
        else:
            self.assertIsNone(data.end_date)
            self.assertIsNone(data.end_date_precision)

        if 'ended' in json_data:
            self.assertEquals(json_data['ended'], data.ended)
        else:
            self.assertFalse(data.ended)

        if 'country_id' in json_data:
            self.assertEquals(json_data['country_id'], data.country_id)
        else:
            self.assertIsNone(data.country_id)

        if 'gender' in json_data:
            self.assertEquals(
                json_data['gender']['gender_id'],
                data.gender_id
            )
        else:
            self.assertIsNone(data.gender)

    def put_data_check_specific(self, json_data, old_data, new_data):
        if 'begin_date' in json_data:
            self.put_post_check_date_json(
                json_data['begin_date'],
                new_data.begin_date,
                new_data.begin_date_precision
            )
        else:
            self.assertEquals(new_data.begin_date, old_data.begin_date)
            self.assertEquals(
                new_data.begin_date_precision,
                old_data.begin_date_precision)

        if 'end_date' in json_data:
            self.put_post_check_date_json(
                json_data['end_date'],
                new_data.end_date,
                new_data.end_date_precision
            )
        else:
            self.assertEquals(new_data.end_date, old_data.end_date)
            self.assertEquals(
                new_data.end_date_precision,
                old_data.end_date_precision)

        if 'ended' in json_data:
            self.assertEquals(json_data['ended'], new_data.ended)
        else:
            self.assertEquals(old_data.ended, new_data.ended)

        if 'country_id' in json_data:
            self.assertEquals(json_data['country_id'], new_data.country_id)
        else:
            self.assertEquals(old_data.country_id, new_data.country_id)

        if 'gender' in json_data:
            self.assertEquals(
                json_data['gender']['gender_id'],
                new_data.gender_id
            )
        else:
            self.assertEquals(old_data.gender, new_data.gender)

