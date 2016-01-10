# -*- coding: utf8 -*-

# Copyright (C) 2015 Stanisław Szcześniak

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

import datetime
import json
import random
import uuid

from bbschema import create_all
from werkzeug.test import Headers

from bbws import create_app, db
from constants import *
from get_bbid_testing import GetBBIDTests
from get_list_testing import GetListTests
from delete_testing import DeleteTests
from put_testing import PutTests
from post_testing import PostTests
from .fixture import load_data
from .sample_data_helper_functions import get_other_type_values


class EntityTestCases(GetBBIDTests, GetListTests, DeleteTests,
                      PutTests, PostTests):
    def create_app(self):
        self.app = create_app('../config/test.py')
        return self.app

    # noinspection PyPep8Naming
    def setUp(self):
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")
        db.engine.execute("CREATE SCHEMA bookbrainz")
        create_all(db.engine)

        random.seed()
        load_data(db)

        response = self.client.post(
            '/oauth/token',
            data={
                'client_id': '9ab9da7e-a7a3-4f86-87c6-bf8b4b8213c7',
                'username': 'Bob',
                'password': "bb",
                'grant_type': 'password'
            })

        self.assert200(response)
        oauth_access_token = response.json.get(u'access_token')

        self.request_default_headers = Headers(
            [('Authorization', 'Bearer ' + oauth_access_token),
             ('Content-Type', 'application/json')])

        self.specific_setup()

        self.specific_names = {}
        self.set_specific_names()
        # TODO add checking for specific names

    # noinspection PyPep8Naming
    def tearDown(self):
        db.session.remove()
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")

    def specific_setup(self):
        raise NotImplementedError

    def prepare_put_data(self, instance):
        raise NotImplementedError

    def prepare_post_data(self):
        raise NotImplementedError

    def set_specific_names(self):
        raise NotImplementedError

    def bbid_one_get_tests_specific_check(self, instance, response):
        raise NotImplementedError

    def post_data_check_specific(self, json_data, data):
        raise NotImplementedError

    def is_debug_mode(self):
        return True

    def get_specific_name(self, key):
        return self.specific_names[key]

    def get_request_default_headers(self):
        return self.request_default_headers

    def put_tests(self):
        for i in range(PUT_TESTS_GOOD_COUNT):
            self.put_good_tests()
        # for i in range(PUT_TESTS_BAD_COUNT):
        #   self.put_post_bad_tests('put')
        """ Commented for now, because bad type requests
            are triggering exceptions and not HTTP 400 (same as in the POST)
            [see ws_bugs.md]
        """

    def put_good_tests(self):
        instances_db = \
            db.session.query(self.get_specific_name('entity_class')).all()
        if len(instances_db) == 0:
            return
        rand_pos = random.randint(0, len(instances_db) - 1)
        random_instance = instances_db[rand_pos]
        random_instance_to_check = \
            db.session.query(self.get_specific_name('entity_class'))\
            .filter(
                self.get_specific_name('entity_class').entity_gid ==
                random_instance.entity_gid)\
            .one()\
            .master_revision.entity_data
        data_to_pass = self.prepare_put_data(random_instance)

        response_ws = \
            self.client.put('/{}/{}/'.format(
                self.get_specific_name('ws_name'),
                unicode(random_instance.entity_gid)),
                headers=self.request_default_headers,
                data=json.dumps(data_to_pass))
        self.assert200(response_ws)

        instances_db_after = \
            db.session.query(self.get_specific_name('entity_class')).all()

        self.assertEquals(len(instances_db), len(instances_db_after))

        instances_db.sort(key=lambda x: x.entity_gid)
        instances_db_after.sort(key=lambda x: x.entity_gid)

        changed_instance = None

        for i in range(len(instances_db_after)):
            if instances_db_after[i].entity_gid == random_instance.entity_gid:
                changed_instance = instances_db_after[i]
                del instances_db[i]
                del instances_db_after[i]
                break

        self.assertEquals(instances_db, instances_db_after)
        self.check_json_data_and_instance(
            data_to_pass,
            random_instance_to_check,
            changed_instance)

    # TODO make this function and equality_check_lists clearer
    def check_json_data_and_instance(self, passed_data_dict,
                                     added_instance_before,
                                     added_instance_now):

        self.equality_check_ws(passed_data_dict, added_instance_now)
        self.equality_check_lists(passed_data_dict, added_instance_before,
                                  added_instance_now)

    def equality_check_lists(self, data_ws, data_db_before, data_db_after):
        self.check_aliases(data_ws, data_db_before, data_db_after)

    def check_aliases(self, data_ws, data_db_before, data_db_after):

        aliases_json, updated_aliases = self.determine_aliases(data_ws)
        db_aliases_before, db_aliases_after = \
            self.get_aliases_before_and_after(data_db_before, data_db_after)

        for alias_id in updated_aliases:
            alias_json = updated_aliases[alias_id]

            self.assertTrue(len([alias for alias in db_aliases_before
                                 if alias.alias_id == alias_id]))
            for i in range(len(db_aliases_before)):
                if db_aliases_before[i].alias_id == alias_id:
                    to_delete = i
                    break
            del db_aliases_before[to_delete]

            if alias_json is not None:
                self.assertTrue(len([alias for alias in db_aliases_after
                                if alias.name == alias_json[u'name']]) == 1)
                for i in range(len(db_aliases_after)):
                    if db_aliases_after[i].name == alias_json[u'name']:
                        to_delete = i
                        break

                self.equality_check_alias_ws_db(alias_json,
                                                db_aliases_after[to_delete])

                del db_aliases_after[to_delete]
            else:
                self.assertTrue(len([alias for alias in db_aliases_after
                                     if alias.alias_id == alias_id]) == 0)

        for alias in aliases_json:
            to_delete = -1
            for i in range(len(db_aliases_after)):
                if _name_or_sort_name(db_aliases_after[i]) == \
                        _name_or_sort_name(alias):
                    self.assertEquals(to_delete, -1)
                    to_delete = i
            self.assertNotEquals(to_delete, -1)
            self.equality_check_alias_ws_db(alias, db_aliases_after[to_delete])
            del db_aliases_after[to_delete]

        db_aliases_before.sort(key=lambda x: _name_or_sort_name(x))
        db_aliases_after.sort(key=lambda x: _name_or_sort_name(x))

        self.assertEquals(db_aliases_before, db_aliases_after)

    def determine_aliases(self, data_ws):
        updated_aliases = {}
        json_aliases = []
        if u'aliases' in data_ws:
            json_aliases = data_ws[u'aliases']
            if json_aliases not in [None, []]:
                if type(json_aliases[0]) == dict:
                    json_aliases.sort(key=lambda x: _name_or_sort_name(x))
                else:
                    json_aliases = []
                    for alias_id, alias_json in data_ws[u'aliases']:
                        if alias_id is None:
                            json_aliases.append(alias_json)
                        else:
                            self.assertFalse(alias_id in updated_aliases)
                            updated_aliases[alias_id] = alias_json
        return json_aliases, updated_aliases

    def get_aliases_before_and_after(self, data_db_before, data_db_after):
        db_aliases_before = []
        if data_db_before is not None:
            self.assertTrue(hasattr(data_db_before, 'aliases'))
            db_aliases_before = list(data_db_before.aliases)
            db_aliases_before.sort(key=lambda x: _name_or_sort_name(x))

        db_aliases_after = []
        if data_db_after is not None:
            db_aliases_after = list(
                data_db_after.master_revision.entity_data.aliases)
            db_aliases_after.sort(key=lambda x: _name_or_sort_name(x))

        return db_aliases_before, db_aliases_after

    def equality_check_alias_ws_db(self, alias_json, alias_db):
        if u'sort_name' in alias_json:
            self.assertEquals(alias_json[u'sort_name'], alias_db.sort_name)

        if u'name' in alias_json:
            self.assertEquals(alias_json[u'name'], alias_db.name)

        if u'language_id' in alias_json:
            self.assertEquals(alias_json[u'language_id'], alias_db.language_id)

        if u'primary' in alias_json:
            self.assertEquals(alias_json[u'primary'], alias_db.primary)

    def put_post_bad_tests(self, type_of_query):
        put_instance = None
        if type_of_query == 'post':
            used_data = self.prepare_post_data()
        else:
            instances_db = \
                db.session.query(self.get_specific_name('entity_class')).all()
            self.assertGreater(len(instances_db), 0)
            put_instance = random.choice(instances_db)
            used_data = self.prepare_put_data(put_instance)

        for key in used_data:
            bad_values_list = get_other_type_values(used_data[key])
            for bad_value in bad_values_list:

                data_to_pass = used_data.copy()
                data_to_pass[key] = bad_value

                self.put_post_bad_data_test(
                    json.dumps(data_to_pass),
                    type_of_query, put_instance)

        data_to_pass_json_bad = list(json.dumps(used_data.copy()))

        self.assertTrue(',' in data_to_pass_json_bad)
        for i in range(len(data_to_pass_json_bad)):
            if data_to_pass_json_bad[i] == ',':
                data_to_pass_json_bad[i] = '.'

        self.put_post_bad_data_test(''.join(data_to_pass_json_bad),
                                    type_of_query, put_instance)

    def put_post_bad_data_test(self, data_to_pass, type_of_query,
                               put_instance=None):

        info_before = [[x.entity_gid, x.last_updated] for x in
            db.session.query(self.get_specific_name('entity_class'))
            .all()]

        response_ws = None
        if type_of_query == 'put':
            response_ws = \
                self.client.put(
                    '/{}/{}/'.format(
                        self.get_specific_name('ws_name'),
                        unicode(put_instance.entity_gid)),
                    headers=self.request_default_headers,
                    data=data_to_pass)

        else:
            response_ws = self.client.post(
                '/' + self.get_specific_name('ws_name') + '/',
                headers=self.request_default_headers,
                data=data_to_pass)

        self.assert400(response_ws)

        instances_db_after =\
            db.session.query(self.get_specific_name('entity_class')).all()
        instances_db_after.sort(key=lambda element: element.entity_gid)

        info_before.sort()

        self.assertTrue(len(info_before), len(instances_db_after))
        for i in range(len(info_before)):
            self.assertEquals(info_before[1],
                              instances_db_after[i].last_updated)
            self.assertEquals(info_before[0], instances_db_after[i].entity_gid)
            self.assertNotEquals(
                instances_db_after[i].master_revision.entity_data, None)

    def equality_check_ws(self, ws_object, db_object, entity_gid=''):
        if _is_simply_comparable(ws_object) and \
                _is_simply_comparable(db_object):
            self.equality_simply_objects_check(ws_object, db_object)
        else:
            try:
                self.assertEquals(_is_simply_comparable(ws_object),
                                  _is_simply_comparable(db_object))
            except:
                raise ValueError(
                    '_is_simply_comparable(ob1) != '
                    '_is_simply_comparable(ob2)\n ob1 = {ob1},\n ob2 = {ob2}'
                    .format(ob1=ws_object, ob2=db_object))

            if type(ws_object) == dict and u'objects' in ws_object:
                self.equality_check_ws(ws_object['objects'], db_object)
            elif type(ws_object) == dict:
                self.equality_check_dict_and_instance(ws_object, db_object,
                                                      entity_gid)
            elif type(ws_object) == list:
                self.equality_check_list_and_list(ws_object, db_object,
                                                  entity_gid)
            else:
                raise ValueError(
                    'Bad types in equality_check_ws '
                    'ws_object {a} db_object {b}'.
                    format(a=ws_object, b=db_object))

    def equality_check_json_and_database_data(self, json_data, db_data,
                                              type_of_data):
        if type_of_data == 'whole_entity':
            self.mutual_entity_check_json_db_data(json_data, db_data)
        elif type_of_data == 'entity_data':
            self.mutual_entity_data_check(json_data, db_data)

    def mutual_entity_check_json_db_data(self, json_data, db_data):
        self.assertEquals(json_data['entity_gid'], db_data.entity_gid)

    def mutual_entity_data_check(self, json_data, db_data, put_or_post=True):
        db_entity_data = db_data.master_revision.entity_data
        if put_or_post:
            self.check_equality_if_exists(json_data, 'annotation',
                              db_entity_data.annotation)
            self.check_equality_if_exists(json_data, 'disambiguation',
                              db_entity_data.disambiguation)
            self.check_equality_if_exists_aliases(json_data,
                                                  db_entity_data.aliases)

        self.check_revision(json_data, db_data)

    def check_revision(self, json_data, db_data):
        pass

    def check_equality_if_exists(self, json_dict, key, db_value):
        if key in json_dict:
            self.assertEquals(json_dict[key], db_value)

    def check_equality_if_exists_aliases(self, json_dict, db_value):
        pass

    def equality_simply_objects_check(self, ws_object, db_object):
        if ws_object is None:
            return
        if type(db_object) == datetime.date:
            return self.equality_check_dates(ws_object, db_object)
        elif type(db_object) == datetime.datetime:
            self.assertEquals(unicode(ws_object),
                              unicode(db_object.isoformat()))
        else:
            self.assertEquals(unicode(ws_object), unicode(db_object))

    def equality_check_dates(self, ws_object, db_object):
        self.assertEquals((ws_object is None), (db_object is None))

        ws_str_date = unicode(ws_object)
        db_str_date = unicode(db_object.isoformat())

        return db_str_date.startswith(ws_str_date)

    def equality_check_dict_and_instance(self, dict_object, db_object,
                                         entity_gid):
        if dict_object is not None and 'entity_gid' in dict_object:
            entity_gid = dict_object['entity_gid']
        if type(dict_object) == dict:
            for key in dict_object.keys():
                if key in [u'aliases', u'identifiers', u'languages',
                           u'relationships']:
                    continue
                if key == 'gender':
                    if dict_object['gender'] == None:
                        self.assertEquals(
                            db_object.master_revision.entity_data.gender_id,
                            None)
                    else:
                        self.equality_simply_objects_check(
                            dict_object['gender']['gender_id'],
                            db_object.master_revision
                            .entity_data.gender_id)

                elif not _is_uri(key):
                    self.equality_check_ws(dict_object[key],
                                           _get_key_from_instance(
                                               db_object, key),
                                           entity_gid)
                else:
                    self.check_uri(dict_object, key, entity_gid)

    def equality_check_list_and_list(self, ws_object, db_object, entity_gid):
        self.assertEquals(len(ws_object), len(db_object))
        if len(ws_object) == 0:
            return
        key_to_sort = _find_attribute_for_sorting(ws_object[0])
        ws_object.sort(key=lambda x: x[key_to_sort])
        db_object.sort(key=lambda x: getattr(x, key_to_sort))

        for i in range(len(ws_object)):
            self.equality_check_ws(ws_object[i], db_object[i], entity_gid)

    def check_uri(self, ws_object, key_uri, entity_gid):
        if key_uri in ['entity_uri', 'uri']:
            return

        my_type = ''
        for type_of_uri in ['aliases', 'annotation', 'relationships',
                            'identifiers', 'disambiguation', 'entity',
                            'editions', '']:
            if type_of_uri in key_uri:
                my_type = type_of_uri
                break
        if my_type != 'relationships':
            to_search = '/' + self.get_specific_name('ws_name') + '/'
        else:
            to_search = '/entity/'
        to_search += entity_gid + '/' + my_type
        to_get = my_type
        if my_type is not '':
            to_get += '_'
        to_get += 'uri'
        text = ws_object[unicode(to_get)]

        self.assertTrue(to_search in text)


def _get_key_from_instance(instance, key):
    if key == 'count':
        return len(instance)
    if key == 'revision':
        return instance.master_revision
    if key == 'gender':
        return instance.master_revision.entity_data.gender_id
    if hasattr(instance, key):
        return getattr(instance, key)

    if not hasattr(instance, 'master_revision'):
        _key_was_not_found(key)

    if hasattr(instance.master_revision, key):
        return getattr(instance.master_revision, key)

    if not hasattr(instance.master_revision, 'entity_data'):
        _key_was_not_found(key)

    if hasattr(getattr(instance.master_revision.entity_data, key), 'content'):
        return getattr(instance.master_revision.entity_data, key).content

    if hasattr(getattr(instance.master_revision.entity_data, key), 'comment'):
        return getattr(instance.master_revision.entity_data, key).comment

    if hasattr(instance.master_revision.entity_data, key):
        return getattr(instance.master_revision.entity_data, key)
    return _key_was_not_found(key)


def _key_was_not_found(key):
    raise KeyError(
        "Couldn't find key {key_val} in database instance".format(key_val=key))


def _is_simply_comparable(object_to_check):
    if object_to_check is None:
        return True
    else:
        return type(object_to_check) in [int, str, uuid.UUID, unicode,
                                         datetime.date, bool,
                                         datetime.datetime]


def _is_uri(string):
    return string in [u'uri', u'annotation_uri', u'disambiguation_uri',
                      u'relationships_uri', u'aliases_uri',
                      u'identifiers_uri', u'entity_uri', u'editions_uri']


def _find_attribute_for_sorting(list_object):
    if u'entity_gid' in list_object:
        return 'entity_gid'
    else:
        for key in list_object.keys():
            if key.endswith('id'):
                return key
    raise ValueError('Can\'t find an id attribute for sorting')


def _name_or_sort_name(element):
    if type(element) == dict:
        if u'name' in element:
            return element[u'name']
        else:
            return element[u'sort_name']
    else:
        if hasattr(element, 'name'):
            return element.name
        else:
            return element.sort_name

