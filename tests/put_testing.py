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

import logging

from flask_testing import TestCase

from check_helper_functions import *
from constants import *


class PutTests(TestCase):
    def get_specific_key(self, name):
        raise NotImplementedError

    def get_request_default_headers(self):
        raise NotImplementedError

    def prepare_put_data(self, instance):
        raise NotImplementedError

    def put_data_check_specific(self, json_data, old_data, new_data):
        raise NotImplementedError

    def put_tests(self):
        logging.info(
            'PUT request tests for {} good tests:{} bad tests:{}'
            .format(
                self.get_specific_key('type_name'),
                PUT_TESTS_GOOD_COUNT,
                PUT_TESTS_BAD_COUNT
            )
        )

        for i in range(PUT_TESTS_GOOD_COUNT):
            logging.info(' Good test #{}'.format(i + 1))
            self.put_good_test()

        """
            Commented for now, because requests with incorrect type values
            are triggering exceptions and not sending HTTP 400 signal
            [see ws_bugs.md]
        """
        """
        for i in range(PUT_TESTS_BAD_COUNT):
            logging.info(' Bad test #{}'.format(i + 1))
            put_post_bad_test(self, 'put')
        """

    def make_put_request(self, entity, data_to_pass):
        response_ws = \
            self.client.put(
                '/{}/{}/'
                .format(
                    self.get_specific_key('ws_name'),
                    unicode(entity.entity_gid)),
                headers=self.get_request_default_headers(),
                data=json.dumps(data_to_pass))
        self.assert200(response_ws)
        return response_ws

    def put_good_test(self):
        entities = \
            db.session.query(self.get_specific_key('entity_class')).all()
        entities_revisions_before = \
            [x.master_revision for x in entities]

        entity = random.choice(entities)
        data_to_pass = self.prepare_put_data(entity)
        self.make_put_request(entity, data_to_pass)

        entities = \
            db.session.query(self.get_specific_key('entity_class')).all()
        entities_revisions_after = \
            [x.master_revision for x in entities]

        entities_revisions_before_revision_ids = \
            set([x.revision_id for x in entities_revisions_before])

        new_revision = \
            [x for x in entities_revisions_after if
             x.revision_id not in entities_revisions_before_revision_ids]

        self.assertEquals(len(new_revision), 1)
        new_revision = new_revision[0]

        updated_entity_revision_before = \
            [x for x in entities_revisions_before
             if x.entity_gid == new_revision.entity_gid]

        self.assertEquals(len(updated_entity_revision_before), 1)
        updated_entity_revision_before = updated_entity_revision_before[0]

        updated_entity_revision_after = \
            [x for x in entities_revisions_after
             if x.entity_gid == new_revision.entity_gid]
        self.assertEquals(len(updated_entity_revision_after), 1)
        updated_entity_revision_after = updated_entity_revision_after[0]

        self.put_data_check(
            data_to_pass,
            updated_entity_revision_before,
            updated_entity_revision_after
        )

    def put_data_check(self, json_data, revision_old, revision_new):
        entity_data_old = revision_old.entity_data
        entity_data_new = revision_new.entity_data

        self.put_data_check_basic(
            json_data,
            entity_data_old,
            entity_data_new
        )

        self.put_data_check_specific(
            json_data,
            entity_data_old,
            entity_data_new
        )

    def put_data_check_basic(self, json_data, data_old, data_new):
        default_args = (json_data, data_old, data_new)

        self.put_check_disambiguation(*default_args)
        self.put_check_annotation(*default_args)
        self.put_data_check_aliases(*default_args)
        self.put_data_check_identifiers(*default_args)

    def put_check_disambiguation(self, json_data, data_old, data_new):
        if 'disambiguation' in json_data:
            self.assert_equals_put(
                json_data['disambiguation'],
                getattr(data_new.disambiguation, 'comment', None)
            )
        else:
            self.assertEquals(
                getattr(data_old.disambiguation, 'comment', None),
                getattr(data_new.disambiguation, 'comment', None)
            )

    def put_check_annotation(self, json_data, data_old, data_new):
        if 'annotation' in json_data:
            self.assert_equals_put(
                json_data['annotation'],
                getattr(data_new.annotation, 'content', None)
            )
        else:
            self.assertEquals(
                getattr(data_old.annotation, 'content', None),
                getattr(data_new.annotation, 'content', None)
            )

    def put_data_check_aliases(self, json_data, data_old, data_new):
        if 'aliases' in json_data:
            json_aliases = json_data['aliases']

            removed_aliases = set([x for x, y in json_aliases if y is None])
            added_aliases = [y for x, y in json_aliases if x is None]
            updated_aliases = [[x, y] for x, y in json_aliases
                               if not (x is None or y is None)]
            updated_aliases_ids = [x for x, y in updated_aliases]

            old_aliases = data_old.aliases
            new_aliases = [[alias, False] for alias in data_new.aliases]

            self.assertEquals(
                len(new_aliases),
                len(old_aliases) + len(added_aliases) - len(removed_aliases)
            )

            left_aliases_ids = [alias.alias_id for alias in old_aliases
                                if (alias.alias_id not in removed_aliases and
                                    alias.alias_id not in
                                    updated_aliases_ids)]

            for alias in left_aliases_ids:
                occurrences = [x for x in new_aliases
                               if x[0].alias_id == alias]
                self.assertEquals(len(occurrences), 1)
                self.assertFalse(occurrences[0][1])
                occurrences[0][1] = True

            for alias in added_aliases:
                occurrences = [x for x in new_aliases
                               if x[0].name == alias['name']]
                self.assertEquals(len(occurrences), 1)
                self.assertFalse(occurrences[0][1])
                occurrences[0][1] = True

            for alias_id, alias_json in updated_aliases:
                occurrences = [x for x in new_aliases
                               if x[0].name == alias_json['name']]
                self.assertEquals(len(occurrences), 1)
                self.assertFalse(occurrences[0][1])
                occurrences[0][1] = True
                new_alias = occurrences[0][0]
                check_single_alias_json(self, alias_json, new_alias)

        else:
            self.assertEquals(len(data_old.aliases), len(data_new.aliases))

            data_old.aliases.sort(key=lambda x: x.alias_id)
            data_new.aliases.sort(key=lambda x: x.alias_id)

            for i in range(len(data_old.aliases)):
                self.put_data_check_two_aliases(
                    data_old.aliases[i],
                    data_new.aliases[i])

    def put_data_check_two_aliases(self, a, b):
        for attr in ['alias_id', 'name', 'sort_name', 'primary']:
            self.assertEquals(getattr(a, attr), getattr(b, attr))

    def put_data_check_identifiers(self, json_data, data_old, data_new):
        old_identifiers = data_old.identifiers
        new_identifiers = [[x, False] for x in data_new.identifiers]

        if 'identifiers' in json_data:
            json_identifiers = json_data['identifiers']

            deleted_identifiers = \
                set([x[0] for x in json_identifiers if x[1] == None])
            added_identifiers = [x[1] for x in json_identifiers if x[0] == None]
            updated_identifiers = [[x, y] for x, y in json_identifiers
                                   if not (x is None or y is None)]
            updated_identifiers_ids = [x for x, y in updated_identifiers]

            left_identifiers_ids = \
                [x.identifier_id for x in old_identifiers
                 if (x.identifier_id not in deleted_identifiers) and
                 x.identifier_id not in updated_identifiers_ids]

            self.assertEquals(
                len(new_identifiers),
                len(old_identifiers) + len(added_identifiers) -
                len(deleted_identifiers)
            )

            for identifier in left_identifiers_ids:
                occurrences = \
                    [x for x in new_identifiers
                     if x[0].identifier_id == identifier]
                self.assertEquals(len(occurrences), 1)
                self.assertFalse(occurrences[0][1])
                occurrences[0][1] = True

            for identifier in added_identifiers:
                occurrences = [x for x in new_identifiers
                               if x[0].value == identifier['value']]
                self.assertEquals(len(occurrences), 1)
                self.assertFalse(occurrences[0][1])
                occurrences[0][1] = True

            for identifier_id, identifier_json in updated_identifiers:
                occurrences = [x for x in new_identifiers
                               if x[0].value == identifier_json['value']]
                self.assertEquals(len(occurrences), 1)
                self.assertFalse(occurrences[0][1])
                occurrences[0][1] = True

                new_identifier = occurrences[0][0]
                # TODO remove try, except after fixing BB-169
                try:
                    self.assertEquals(
                        identifier_hash(identifier_json, True),
                        identifier_hash(new_identifier, False)
                    )
                except:
                    pass
        else:
            new_identifiers = [x for x in data_new.identifiers]
            old_identifiers.sort(key=lambda x: x.identifier_id)
            new_identifiers.sort(key=lambda x: x.identifier_id)
            self.assertEquals(old_identifiers, new_identifiers)

    def put_data_check_languages_json(self, json_data, old_data, new_data):
        old_languages_ids = [x.id for x in old_data.languages]
        new_languages_ids = [x.id for x in new_data.languages]
        if 'languages' in json_data:
            added_languages = [x[1] for x in json_data['languages']
                               if x[0] == None]

            old_languages_ids.extend(added_languages)

            removed_languages = [x[0] for x in json_data['languages']
                                 if x[1] == None]

            old_languages_ids = [x for x in old_languages_ids
                                 if x not in removed_languages]

        old_languages_ids.sort()
        new_languages_ids.sort()
        self.assertEquals(old_languages_ids, new_languages_ids)

    # temporary version until the bug is solved
    # putting a null value should delete the old value, but it doesn't
    # see bugs_ws.md
    def assert_equals_put(self, a, b):
        if a is not None:
            self.assertEquals(a, b)
