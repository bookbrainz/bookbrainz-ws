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

import inspect
import json
import random

from bbschema import Language, Gender, IdentifierType

from bbws import db
from sample_data_helper_functions import get_other_type_values


def assert_equals_or_both_none(test_case_object, dictionary, key, value,
                               check_function=None, empty_list_allowed=False):
    if key in dictionary:
        if check_function is None:
            test_case_object.assertEquals(dictionary[key], value)
        else:
            if not inspect.ismethod(check_function):
                check_function(test_case_object, dictionary[key], value)
            else:
                check_function(dictionary[key], value)
    else:
        if empty_list_allowed:
            test_case_object.assertTrue(value in [None, []])
        else:
            test_case_object.assertIsNone(value)


def check_uri_suffix(test_case_object, value, suffix, is_none=False):
    if not is_none:
        test_case_object.assertTrue(value.endswith(suffix))
    else:
        test_case_object.assertIsNone(value)


def get_one_entity_type(test_case_object, db, entity_type_class,
                        entity_type_id_string, gid):
    results = db.session.query(entity_type_class) \
        .filter(getattr(entity_type_class, entity_type_id_string) == gid) \
        .all()
    test_case_object.assertEquals(len(results), 1)
    return results[0]


def get_language(test_case_object, db, lang_id):
    results = db.session.query(Language) \
        .filter(Language.id == lang_id) \
        .all()
    test_case_object.assertEquals(len(results), 1)
    return results[0]


def get_gender(test_case_object, db, gender_id):
    results = db.session.query(Gender) \
        .filter(Gender.id == gender_id) \
        .all()
    test_case_object.assertEquals(len(results), 1)
    return results[0]


def check_date_json(test_case_object, json_date, json_date_precision,
                    date, date_precision, check_date_none=True):
    if json_date is None and check_date_none is True:
        test_case_object.assertIsNone(date)
    else:
        date_iso = date.isoformat()
        y, m, d = date_iso.split('-')
        jy, jm, jd = -1, -1, -1
        test_case_object.assertEquals(
            json_date_precision,
            date_precision
        )
        if json_date_precision is not None:
            test_case_object.assertEquals(
                date_precision_id_to_precision_name(len(json_date.split('-'))),
                json_date_precision
            )

        if json_date_precision == 'YEAR':
            jy = json_date
            precision_id = 1
        elif json_date_precision == 'MONTH':
            jy, jm = json_date.split('-')
            precision_id = 2
        else:
            jy, jm, jd = json_date.split('-')
            precision_id = 3

        test_case_object.assertEquals(int(jy), int(y))
        if precision_id > 1:
            test_case_object.assertEquals(int(jm), int(m))
        if precision_id > 2:
            test_case_object.assertEquals(int(jd), int(d))


def date_precision_id_to_precision_name(precision_id):
    return ['YEAR', 'MONTH', 'DAY'][precision_id - 1]


def check_gender_json(test_case_object, json_gender, gender):
    if json_gender is not None:
        test_case_object.assertEquals(
            json_gender['gender_id'],
            gender.id
        )
        test_case_object.assertEquals(
            json_gender['name'],
            gender.name
        )
    else:
        test_case_object.assertIsNone(gender)


def check_country_id(test_case_object, json_data, country_id):
    if 'country_id' in json_data and \
            json_data['country_id'] is not None:
        test_case_object.assertEquals(
            json_data['country_id'],
            country_id
        )
    else:
        test_case_object.assertIsNone(country_id)


def check_languages_json(test_case_object, json_languages, languages):
    test_case_object.assertEquals(len(json_languages), len(languages))

    json_languages.sort(key=lambda x: x['language_id'])
    languages.sort(key=lambda x: x.id)

    for i in range(len(json_languages)):
        check_one_language_json(
            test_case_object,
            json_languages[i],
            languages[i]
        )


def check_one_language_json(test_case_object, json_lang, lang):
    test_case_object.assertEquals(json_lang['language_id'], lang.id)
    test_case_object.assertEquals(json_lang['name'], lang.name)


def identifier_hash(identifier, is_json):
    if is_json:
        type_id = identifier \
            .get('identifier_type', {}) \
            .get('identifier_type_id')
        value = identifier \
            .get('value')
    else:
        type_id = identifier.identifier_type_id
        value = identifier.value
    return type_id.__hash__() * (int(1e100)) + value.__hash__()


def check_entity_type_json(test_case_object, instance, json_data):
    entity_type_string = test_case_object.get_specific_key('entity_type')
    if entity_type_string is None:
        return

    entity_type_id_string = test_case_object.get_specific_key('entity_type_id')
    entity_type_class = test_case_object.get_specific_key('entity_type_class')
    if entity_type_string in json_data and \
            not json_data[entity_type_string] is None:
        test_case_object.assertEquals(
            json_data[entity_type_string][entity_type_id_string],
            getattr(instance.master_revision.entity_data,
                    entity_type_id_string))
        entity_type = get_one_entity_type(
            test_case_object,
            db,
            entity_type_class,
            entity_type_id_string,
            json_data[entity_type_string][entity_type_id_string]
        )
        test_case_object.assertEquals(
            json_data[entity_type_string].get('label', entity_type.label),
            entity_type.label
        )
    else:
        test_case_object.assertIsNone(getattr(
            instance.master_revision.entity_data, entity_type_string))


def put_post_bad_test(test_case, type_of_query):
    put_instance = None
    if type_of_query == 'post':
        used_data = test_case.prepare_post_data()
    else:
        instances_db = \
            db.session.query(test_case.get_specific_key('entity_class')).all()
        test_case.assertGreater(len(instances_db), 0)
        put_instance = random.choice(instances_db)
        used_data = test_case.prepare_put_data(put_instance)

    for key in used_data:
        bad_values_list = get_other_type_values(used_data[key])
        for bad_value in bad_values_list:

            data_to_pass = used_data.copy()
            data_to_pass[key] = bad_value

            test_case.put_post_bad_data_test(
                json.dumps(data_to_pass),
                type_of_query, put_instance)

    data_to_pass_json_bad = list(json.dumps(used_data.copy()))

    test_case.assertTrue(',' in data_to_pass_json_bad)
    for i in range(len(data_to_pass_json_bad)):
        if data_to_pass_json_bad[i] == ',':
            data_to_pass_json_bad[i] = '.'

    test_case.put_post_bad_data_test(''.join(data_to_pass_json_bad),
                                     type_of_query, put_instance)


def put_post_bad_data_test(test_case, data_to_pass, type_of_query,
                           put_instance=None):
    info_before = \
        [[x.entity_gid, x.last_updated] for x in db.session.query(
            test_case.get_specific_key('entity_class')).all()]

    if type_of_query == 'put':
        response_ws = \
            test_case.client.put(
                '/{}/{}/'.format(
                    test_case.get_specific_key('ws_name'),
                    unicode(put_instance.entity_gid)),
                headers=test_case.get_request_default_headers(),
                data=data_to_pass)

    else:
        response_ws = test_case.client.post(
            '/' + test_case.get_specific_key('ws_name') + '/',
            headers=test_case.get_request_default_headers(),
            data=data_to_pass)

    test_case.assert400(response_ws)

    instances_db_after = \
        db.session.query(test_case.get_specific_key('entity_class')).all()
    instances_db_after.sort(key=lambda element: element.entity_gid)

    info_before.sort()

    test_case.assertTrue(len(info_before), len(instances_db_after))
    for i in range(len(info_before)):
        test_case.assertEquals(info_before[1],
                               instances_db_after[i].last_updated)
        test_case.assertEquals(info_before[0], instances_db_after[i].entity_gid)
        test_case.assertNotEquals(
            instances_db_after[i].master_revision.entity_data, None)


def check_single_alias_json(test_case, json_alias, alias):
    test_case.assertEquals(json_alias['name'], alias.name)
    test_case.assertEquals(json_alias['sort_name'], alias.sort_name)
    assert_equals_or_both_none(
        test_case,
        json_alias,
        'language_id',
        alias.language_id
    )
    assert_equals_or_both_none(
        test_case,
        json_alias,
        'primary',
        alias.primary,
    )


def check_edition_format_json(test_case, edition_format_json, edition_format):
    if edition_format_json is None:
        test_case.assertIsNone(edition_format)
    else:
        test_case.assertEquals(
            edition_format_json['edition_format_id'],
            edition_format.edition_format_id
        )
        test_case.assertEquals(
            edition_format_json['label'],
            edition_format.label
        )


def check_edition_status_json(test_case, edition_status_json, edition_status):
    if edition_status_json is None:
        test_case.assertIsNone(edition_status)
    else:
        test_case.assertEquals(
            edition_status_json['edition_status_id'],
            edition_status.edition_status_id
        )
        test_case.assertEquals(
            edition_status_json['label'],
            edition_status.label
        )
