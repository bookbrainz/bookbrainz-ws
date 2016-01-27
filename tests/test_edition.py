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

from bbschema import Edition

from check_helper_functions import *
from entity_testing import EntityTests
from sample_data_helper_functions import *

EDITION_SIMPLE_ATTRIBUTES = \
    ['pages', 'width', 'height', 'depth', 'weight', 'country_id']


class TestEdition(EntityTests):
    """Class that gathers tests for Edition entities.

    See class_diagram.png to see how it is related to other classes.
    """
    def specific_setup(self):
        pass

    def set_specific_names(self):
        self.specific_names['entity_class'] = Edition
        self.specific_names['type_name'] = u'Edition'
        self.specific_names['ws_name'] = 'edition'
        self.specific_names['entity_type_id'] = None
        self.specific_names['entity_type'] = None
        self.specific_names['entity_type_class'] = None

    def prepare_put_data(self, instance):
        data = {}

        self.prepare_put_post_not_specific_data(data)

        maybe_add(
            data,
            'publication',
            unicode(random_publication_id())
        )

        mutual_put_data_prepare(data, instance)

        return data

    def prepare_post_data(self):
        data = {}

        self.prepare_put_post_not_specific_data(data)

        maybe_add(
            data,
            'publication',
            unicode(random_publication_id()),
            False
        )

        mutual_post_data_prepare(data)

        return data

    def prepare_put_post_not_specific_data(self, data):
        release_date, release_date_precision = get_string_random_date()
        maybe_add(data, 'release_date', release_date)

        for key in EDITION_SIMPLE_ATTRIBUTES:
            maybe_add(data, key, get_random_physical_integer_value())

        maybe_add(
            data,
            'language',
            {'language_id': random_language_id()}
        )

        maybe_add(
            data,
            'edition_format',
            {'edition_format_id': random_edition_format_id()}
        )

        maybe_add(
            data,
            'edition_status',
            {'edition_status_id': random_edition_format_id()}
        )

        maybe_add(
            data,
            'publisher',
            unicode(random_publisher_id())
        )

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
        entity_data = instance.master_revision.entity_data
        for key in EDITION_SIMPLE_ATTRIBUTES:
            # temporarily
            if key is not 'country_id':
                self.assertEquals(
                    response.json.get(key, None),
                    getattr(entity_data, key, None)
                )

        check_date_json(
            self,
            response.json['release_date'],
            response.json['release_date_precision'],
            entity_data.release_date,
            entity_data.release_date_precision
        )

        check_edition_format_json(
            self,
            response.json.get('edition_format'),
            entity_data.edition_format
        )

        check_edition_status_json(
            self,
            response.json.get('edition_status'),
            entity_data.edition_status
        )

        check_uri_suffix(
            self,
            response.json['publication_uri'],
            '/{}/{}/'.format(
                'publication',
                entity_data.publication_gid,
            ),
            entity_data.publication is None
        )
        check_uri_suffix(
            self,
            response.json['publisher_uri'],
            '/{}/{}/'.format(
                'publisher',
                entity_data.publisher_gid
            ),
            entity_data.publisher is None
        )
        if response.json['language'] is not None:
            check_one_language_json(
                self,
                response.json['language'],
                entity_data.language
            )
        else:
            self.assertIsNone(entity_data.language)

    def post_data_check_specific(self, json_data, data):
        data = data.master_revision.entity_data

        if 'release_date' in json_data:
            self.put_post_check_date_json(
                json_data['release_date'],
                data.release_date,
                data.release_date_precision
            )
        else:
            self.assertIsNone(data.release_date)
            self.assertIsNone(data.release_date_precision)

        for key in EDITION_SIMPLE_ATTRIBUTES:
            if key in json_data:
                self.assertEquals(json_data[key], getattr(data, key))
            else:
                self.assertIsNone(getattr(data, key))

        if 'edition_format' in json_data:
            json_ef = json_data['edition_format']
            ef = data.edition_format
            self.assertEquals(
                json_ef['edition_format_id'],
                ef.edition_format_id
            )
        else:
            self.assertIsNone(data.edition_format)

        if 'edition_status' in json_data:
            json_es = json_data['edition_status']
            es = data.edition_status
            self.assertEquals(
                json_es['edition_status_id'],
                es.edition_status_id
            )
        else:
            self.assertIsNone(data.edition_status)

        if 'language' in json_data:
            self.assertEquals(
                json_data['language']['language_id'],
                data.language.id
            )
        else:
            self.assertIsNone(data.language)

        if 'publisher' in json_data:
            self.assertEquals(
                json_data['publisher'],
                unicode(data.publisher_gid))
        else:
            self.assertIsNone(data.publisher)

        if 'publication' in json_data:
            self.assertEquals(
                json_data['publication'],
                unicode(data.publication_gid)
            )
        else:
            self.assertIsNone(data.publication)

    def put_data_check_specific(self, json_data, old_data, new_data):
        if 'release_date' in json_data:
            self.put_post_check_date_json(
                json_data['release_date'],
                new_data.release_date,
                new_data.release_date_precision
            )
        else:
            self.assertEquals(old_data.release_date, new_data.release_date)
            self.assertEquals(old_data.release_date_precision,
                              new_data.release_date_precision)

        for key in EDITION_SIMPLE_ATTRIBUTES:
            if key in json_data:
                self.assertEquals(json_data[key], getattr(new_data, key))
            else:
                self.assertEquals(
                    getattr(old_data, key),
                    getattr(new_data, key),
                )

        if 'edition_format' in json_data:
            json_ef = json_data['edition_format']
            ef = new_data.edition_format
            self.assertEquals(
                json_ef['edition_format_id'],
                ef.edition_format_id
            )
        else:
            self.assertEquals(
                old_data.edition_format,
                new_data.edition_format
            )

        if 'edition_status' in json_data:
            json_es = json_data['edition_status']
            es = new_data.edition_status
            self.assertEquals(
                json_es['edition_status_id'],
                es.edition_status_id
            )
        else:
            self.assertEquals(
                old_data.edition_status,
                new_data.edition_status
            )

        if 'language' in json_data:
            self.assertEquals(
                json_data['language']['language_id'],
                new_data.language.id
            )
        else:
            self.assertEquals(
                old_data.language,
                new_data.language
            )

        if 'publisher' in json_data:
            self.assertEquals(
                json_data['publisher'],
                unicode(new_data.publisher_gid))
        else:
            self.assertEquals(new_data.publisher, old_data.publisher)

        if 'publication' in json_data:
            self.assertEquals(
                json_data['publication'],
                unicode(new_data.publication_gid)
            )
        else:
            self.assertEquals(new_data.publication, old_data.publication)
