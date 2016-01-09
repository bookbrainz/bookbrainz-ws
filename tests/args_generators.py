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

from sample_data_helper_functions import *
from bbschema import RelationshipEntity, Disambiguation, \
    Annotation, Alias, Relationship
import copy
ma = maybe_add

def no_args_generator():
    return {}


def only_label_args_generator():
    return {'label': get_random_unicode_string()}


def get_languages_args_generator():

    def result_function():
        result = {}
        ma(result, 'name', get_random_unicode_string(), False)
        return result

    return result_function


def get_genders_args_generator():

    def result_function():
        result = {}
        ma(result, 'name', get_random_unicode_string(), False)
        ma(result, 'description', get_random_unicode_string())
        return result

    return result_function


def relationship_type_args_generator():
    result = {}
    result['label'] = get_random_unicode_string()
    result['description'] = get_random_unicode_string()
    result['template'] = get_random_unicode_template()
    return result


def get_creator_data_args_generator(creator_types):
    def result_function():
        result = {}
        mutual_data_generate(result)
        ma(result, 'creator_type_id',
           random.choice(creator_types).creator_type_id)
        ma(result, 'gender_id', random_gender_id())
        ma(result, 'begin_date', random_date())
        ma(result, 'begin_date_precision', random_date_precision())
        ma(result, 'end_date', random_date())
        ma(result, 'end_date_precision', random_date_precision())
        ma(result, 'ended', random.choice([True, False]))
        return result

    return result_function


def get_publisher_data_args_generator(publisher_types):
    def result_function():
        result = {}
        mutual_data_generate(result)
        ma(result, 'publisher_type_id',
            random.choice(publisher_types).publisher_type_id)
        ma(result, 'begin_date', random_date())
        ma(result, 'begin_date_precision', random_date_precision())
        ma(result, 'end_date', random_date())
        ma(result, 'end_date_precision', random_date_precision())
        ma(result, 'ended', random.choice([True, False]))
        return result

    return result_function


def get_publication_data_args_generator(publication_types):
    def result_function():
        result = {}
        ma(result, 'publication_type_id',
            random.choice(publication_types).publication_type_id)
        mutual_data_generate(result)
        return result

    return result_function


def get_work_data_args_generator(work_types, languages):
    def result_function():
        result = {}
        ma(result,'work_type_id', random.choice(work_types).work_type_id)
        ma(result, 'languages', generate_languages(languages))
        mutual_data_generate(result)
        return result

    return result_function


def get_edition_data_args_generator():
    def result_function():
        result = {}
        ma(result, 'pages', random_physical_integer_value())
        ma(result, 'width', random_physical_integer_value())
        ma(result, 'height', random_physical_integer_value())
        ma(result, 'depth', random_physical_integer_value())
        ma(result, 'weight', random_physical_integer_value())
        #TODO complete it
        mutual_data_generate(result)
        return result

    return result_function


def get_relationship_data_args_generator(relationship_types, all_entities):
    def result_function():
        result = {}
        result['relationship_type_id'] =\
            random.choice(relationship_types).relationship_type_id
        ma(result, 'entities', generate_relationship_entities(all_entities))
        #TODO Add entities and texts
        return result

    return result_function


def mutual_data_generate(data):
    ma(data, 'disambiguation',
       Disambiguation(comment=get_random_unicode_string()))
    ma(data, 'annotation', Annotation(content=get_random_unicode_string()))
    ma(data, 'aliases', generate_aliases())


def generate_aliases(min_quantity=0, max_quantity=10):
    aliases_count = randint_extra(min_quantity, max_quantity)
    return [generate_alias() for i in range(aliases_count)]


def generate_languages(languages, max_quantity=10):
    result = []
    for language in languages:
        if len(result) >= max_quantity:
            break
        if random.randint(1, 2) == 1:
            result.append(language)
    return result


def generate_alias():
    return Alias(
        name=get_random_unicode_string(),
        sort_name=get_random_unicode_string(),
        language_id=random_language_id(),
        primary=random.choice([False, True])
    )


def get_entity_revision_args_generator(editor, _entities, _entities_data):
    entities = copy.copy(_entities)
    entities_data = copy.copy(_entities_data)

    def result_function():
        result = {}
        last_entity = entities.pop()
        last_entity_data = entities_data.pop()
        result['user_id'] = editor.user_id
        if type(last_entity) == Relationship:
            result['relationship_id'] = last_entity.relationship_id
            result['relationship_data_id'] = \
                last_entity_data.relationship_data_id
        else:
            result['entity_gid'] = last_entity.entity_gid
            result['entity_data_id'] = last_entity_data.entity_data_id
        return result

    return result_function


def generate_relationship_entities(all_entities):
    result = []
    for i in range(2):
        result.append(generate_single_relationship_entity(i + 1, all_entities))

    if result[0].entity_gid == result[1].entity_gid:
        return generate_relationship_entities(all_entities)

    return result


def generate_single_relationship_entity(position, all_entities):
    return RelationshipEntity(
        entity_gid=random_entity_gid(all_entities), position=position)
