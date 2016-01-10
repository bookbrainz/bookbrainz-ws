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

from bbschema import Language, Gender, Identifier, IdentifierType
from bbws import db
import inspect


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


def check_uri_suffix(test_case_object, value, suffix):
    test_case_object.assertTrue(value.endswith(suffix))


def get_one_entity_type(test_case_object, db, entity_type_class,
                        entity_type_id_string, id):
    results = db.session.query(entity_type_class) \
        .filter(getattr(entity_type_class, entity_type_id_string) == id) \
        .all()
    test_case_object.assertEquals(len(results), 1)
    return results[0]


def get_language(test_case_object, db, id):
    results = db.session.query(Language) \
        .filter(Language.id == id) \
        .all()
    test_case_object.assertEquals(len(results), 1)
    return results[0]


def get_gender(test_case_object, db, id):
    results = db.session.query(Gender) \
        .filter(Gender.id == id) \
        .all()
    test_case_object.assertEquals(len(results), 1)
    return results[0]


def get_identifier_type(test_case_object, db, id):
    results = db.session.query(IdentifierType) \
        .filter(IdentifierType.identifier_type_id == id) \
        .all()
    test_case_object.assertEquals(len(results), 1)
    return results[0]


def check_date_json(test_case_object, json_date, json_date_precision,
                    date, date_precision):
    if json_date is None:
        test_case_object.assertIsNone(date)
    else:
        test_case_object.assertEquals(json_date_precision, date_precision)
        date_iso = date.isoformat()
        y, m, d = date_iso.split('-')
        jy, jm, jd = -1, -1, -1

        test_case_object.assertEquals(
            precision_id_to_precision_name(len(json_date.split('-'))),
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


def precision_id_to_precision_name(precision_id):
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
    entity_type_string = test_case_object.get_specific_name('entity_type')
    entity_type_id_string = test_case_object.get_specific_name('entity_type_id')
    entity_type_class = test_case_object.get_specific_name('entity_type_class')
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
