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

import calendar
import datetime
import random
import uuid

from werkzeug.test import Headers

from constants import *

_genders = []
_languages = []
_creator_types = []
_publisher_types = []
_publication_types = []
_work_types = []
_relationship_types = []
_identifier_types = []
_edition_statuses = []
_edition_formats = []
_publishers = []
_publications = []
_editor = None


def get_other_type_values(arg_value):
    constant_values = [u'UNICODE', 2015, datetime.time(12, 13, 14, 15),
                       uuid.uuid4(), {'revision': {'note': 'some note'}},
                       [1, 2, 3, 4], [], {}, datetime.time(0, 0, 0, 0),
                       Headers([])]
    result_list = []
    for cvalue in constant_values:
        if type(cvalue) != type(arg_value):
            result_list.append(cvalue)
    return result_list


def add_entities(db, entity_class, args_generator=lambda :{},
                 min_quantity=2, max_quantity=DEFAULT_MAX_QUANTITY):
    entities_count = random.randint(min_quantity, max_quantity)
    entities = [entity_class(**(args_generator()))
                for i in range(entities_count)]
    db.session.add_all(entities)
    return entities


__include_ranges_alphabet = [
    (0x1, 0xD7FF),
    (0xE000, 0x10FFFF)
]

__alphabet = [unichr(code_point) for current_range in __include_ranges_alphabet
              for code_point in range(current_range[0], current_range[1] + 1)]


def get_random_unicode_character():
    return random.choice(__alphabet)


def get_random_unicode_string(max_length=DEFAULT_MAX_STRING_SIZE):
    actual_length = random.randint(30, max_length)
    return u''.join(get_random_unicode_character()
                    for i in range(actual_length))


def get_random_unicode_template(max_length=100):
    actual_length = random.randint(0, max_length)
    return_string = u''
    for i in range(actual_length):
        if random.randint(1, 10) == 1:
            return_string = return_string + \
                u'<%= subjects[{x}] %>'.format(x=random.randint(0, 1))
        else:
            return_string = return_string + get_random_unicode_character()
    return return_string


def randint_extra(a, b):
    if random.randint(1, 3) == 1 or a >= b:
        return a
    else:
        return random.randint(a + 1, b)


def get_random_date():
    y = random.randint(datetime.MINYEAR, datetime.MAXYEAR)
    m = random.randint(1, 12)
    d = random.randint(1, calendar.monthrange(y, m)[1])
    return datetime.date(y, m, d)


def get_random_date_precision():
    return random.choice(['YEAR', 'MONTH', 'DAY'])


def get_string_random_date():
    rand_date = get_random_date()
    rand_precision = get_random_date_precision()

    if rand_precision == 'YEAR':
        return_date = '{y}'.format(y=rand_date.year)
    elif rand_precision == 'MONTH':
        return_date = '{y}-{m}'.format(y=rand_date.year, m=rand_date.month)
    else:
        return_date = '{y}-{m}-{d}'.format(
            y=rand_date.year, m=rand_date.month, d=rand_date.day)

    return return_date, rand_precision


def get_random_physical_integer_value():
    return random.randint(0, 1e9)


def get_random_entity_gid(all_entities):
    return random.choice(all_entities).entity_gid


def maybe_add(data, key, value, maybe=True):
    if random_boolean() or not maybe:
        data[key] = value
        return True
    return False


def random_boolean():
    return random.choice([True, False])


def random_language_id():
    return random.choice(_languages).id


def random_language():
    return random.choice(_languages)


def random_gender_id():
    return random.choice(_genders).id


def random_creator_type_id():
    return random.choice(_creator_types).creator_type_id


def random_work_type_id():
    return random.choice(_work_types).work_type_id


def random_publisher_type_id():
    return random.choice(_publisher_types).publisher_type_id


def random_publication_type_id():
    return random.choice(_publication_types).publication_type_id


def random_relationship_type_id():
    return random.choice(_relationship_types).relationship_type_id


def random_identifier_type():
    return random.choice(_identifier_types)


def random_identifier_type_id():
    return random.choice(_identifier_types).identifier_type_id


def random_edition_format_id():
    return random.choice(_edition_formats).edition_format_id


def random_edition_status_id():
    return random.choice(_edition_statuses).edition_status_id


def random_publisher_id():
    return random.choice(_publishers).entity_gid


def random_publication_id():
    return random.choice(_publications).entity_gid


def mutual_put_data_prepare(data, instance):
    maybe_add(data, u'disambiguation', get_random_unicode_string())
    maybe_add(data, u'annotation', get_random_unicode_string())
    maybe_add(data, u'aliases', get_random_put_aliases(instance))
    maybe_add(data, u'identifiers', get_random_put_identifiers(instance))

def get_random_put_aliases(instance):
    if instance.master_revision.entity_data.aliases is not None:
        old_aliases = instance.master_revision.entity_data.aliases
    else:
        old_aliases = []

    result = []

    for alias in old_aliases:
        x = random.randint(1, 4)
        if x == 1:
            result.append([alias.alias_id, get_random_json_alias()])
        elif x == 2:
            result.append([alias.alias_id, None])

    new_aliases_count = randint_extra(0, NEW_ALIASES_MAX_COUNT)
    for i in range(new_aliases_count):
        result.append([None, get_random_json_alias()])

    random.shuffle(result)
    return result


def get_random_json_alias():
    return {
        u'name': get_random_unicode_string(),
        u'sort_name': get_random_unicode_string(),
        u'language_id': random_language_id(),
        u'primary': random_boolean()
    }


def get_random_put_languages(instance):
    if instance.master_revision.entity_data.languages is not None:
        old_languages = instance.master_revision.entity_data.languages
    else:
        old_languages = []

    result = []
    old_languages_ids = []

    for language in old_languages:
        x = random.randint(1, 4)
        if x == 1:
            result.append([language.id, None])
        old_languages_ids.append(language.id)

    new_languages_count = randint_extra(0, NEW_LANGUAGES_MAX_COUNT)
    recently_added_languages = []
    for i in range(new_languages_count):
        random_lang_id = random_language_id()
        if random_lang_id not in (old_languages_ids + recently_added_languages):
            result.append([None, random_lang_id])
            recently_added_languages.append(random_lang_id)
    random.shuffle(result)
    return result


def get_random_put_identifiers(instance):
    ent_data = instance.master_revision.entity_data
    identifiers = ent_data.identifiers
    result = []
    for i in range(len(identifiers)):
        r = random.randint(1,5)
        if r == 1:
            result.append([identifiers[i].identifier_id, None])
        elif r == 2:
            result.append([
                identifiers[i].identifier_id,
                get_single_random_identifier()
            ])

    new_count = randint_extra(0, NEW_IDENTIFIERS_MAX_COUNT)
    new_identifiers =\
    [[None, get_single_random_identifier()] for i in range(new_count)]
    result.extend(new_identifiers)

    return result


def mutual_post_data_prepare(data):
    maybe_add(data, u'disambiguation', get_random_unicode_string())
    maybe_add(data, u'annotation', get_random_unicode_string())
    maybe_add(data, u'aliases', get_random_post_aliases())
    maybe_add(data, u'identifiers', get_random_post_identifiers())


def get_random_post_aliases():
    new_aliases_count = randint_extra(0, NEW_ALIASES_MAX_COUNT)
    return [get_random_json_alias() for i in range(new_aliases_count)]


def get_random_post_languages():
    new_languages_count = randint_extra(0, NEW_LANGUAGES_MAX_COUNT)
    result_ids = []
    for i in range(new_languages_count):
        language_id = random_language_id()
        if language_id not in result_ids:
            result_ids.append(language_id)
    return [{'language_id': x} for x in result_ids]


def get_random_post_identifiers():
    count = randint_extra(0, NEW_IDENTIFIERS_MAX_COUNT)
    return [get_single_random_identifier() for i in range(count)]


def get_single_random_identifier():
    result = {}
    maybe_add(result, 'identifier_type',
              {'identifier_type_id':random_identifier_type_id()}, False)
    maybe_add(result, 'value', get_random_unicode_string(), False)

    return result

def change_one_character(string):
    if len(string) == 0:
        return string
    else:
        pos = random.randint(0, len(string) - 1)
        string_new = string[:pos] + \
            (['L', '!', '#', '^'])[random.randint(0, 3)] + \
            string[(pos + 1):]
        return string_new
