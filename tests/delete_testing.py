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
import random
import uuid

from flask_testing import TestCase

from bbws import db


class DeleteTests(TestCase):
    """Class that gathers tests for delete requests

    See class_diagram.png to see how it is related to other classes.
    """
    def get_specific_key(self, key):
        raise NotImplementedError

    def get_request_default_headers(self):
        raise NotImplementedError

    def is_debug_mode(self):
        raise NotImplementedError

    def delete_tests(self):
        logging.info(
            'DELETE request tests for {} good tests:{} bad tests:{}'
            .format(self.get_specific_key('type_name'), 1, 1)
        )

        logging.info(' Bad test #{}'.format(1))
        self.bad_delete_tests()

        logging.info(' Good test #{}'.format(1))
        self.good_delete_tests()

    def good_delete_tests(self):
        actual_list = \
            db.session.query(self.get_specific_key('entity_class')).all()
        initial_list = [[x.entity_gid, x.last_updated] for x in actual_list]
        initial_size = len(initial_list)
        initial_list.sort()

        while len(actual_list) > 0:
            rand_pos = random.randint(0, len(actual_list) - 1)
            random_instance = actual_list[rand_pos]

            response_ws = self.client.delete(
                '/{entity_type}/{entity_gid}/'.format(
                    entity_type=self.get_specific_key('ws_name'),
                    entity_gid=random_instance.entity_gid),
                headers=self.get_request_default_headers(),
                data="{\"revision\": {\"note\": \"A Test Note\"}}")

            self.assert200(response_ws)

            instances_db_after = \
                db.session.query(self.get_specific_key('entity_class')).all()
            self.assertEquals(len(instances_db_after), initial_size)

            instances_db_after.sort(key=lambda element: element.entity_gid)

            for i in range(len(instances_db_after)):
                self.assertEquals(
                    initial_list[i][0],
                    instances_db_after[i].entity_gid
                )

                if initial_list[i][0] == random_instance.entity_gid:

                    self.assertIsNone(
                        instances_db_after[i].master_revision.entity_data
                    )

                    self.assertGreaterEqual(
                        instances_db_after[i].last_updated,
                        initial_list[i][1]
                    )

            del actual_list[rand_pos]

    def bad_delete_tests(self):
        self.bad_delete_uuid_tests()
        self.bad_delete_format_tests()
        # self.bad_delete_double_tests() Can't be tested now,
        # because there is a bug here [see ws_bugs.md]

    def bad_delete_uuid_tests(self):
        instances_db = \
            db.session.query(self.get_specific_key('entity_class')).all()
        initial_size = len(instances_db)
        for i in range(10):
            entity_gid = uuid.uuid4()
            response_ws = self.client.delete(
                '/{entity_type}/{entity_gid}/'.format(
                    entity_type=self.get_specific_key('ws_name'),
                    entity_gid=entity_gid),
                headers=self.get_request_default_headers(),
                data="{\"revision\": {\"note\": \"A Test Note\"}}")
            self.assert404(response_ws)

            instances_db = \
                db.session.query(self.get_specific_key('entity_class')).all()
            for instance in instances_db:
                self.assertNotEquals(
                    instance.master_revision.entity_data,
                    None
                )
            self.assertEquals(len(instances_db), initial_size)

    def bad_delete_format_tests(self):
        instances_db = \
            db.session.query(self.get_specific_key('entity_class')).all()
        self.assertGreater(len(instances_db), 0)
        rand_pos = random.randint(0, len(instances_db) - 1)
        random_instance = instances_db[rand_pos]

        self.bad_delete_format_single(
            '/creature/{ent_gid}/'
            .format(
                ent_gid=unicode(random_instance.entity_gid)),
            404)

        self.bad_delete_format_single(
            '//////{ent_gid}'
            .format(
                ent_gid=unicode(random_instance.entity_gid)),
            404)

        self.bad_delete_format_single(
            '/{ent_gid}'
            .format(
                ent_gid=unicode(random_instance.entity_gid)),
            404)

        self.bad_delete_format_single(
            '/{ent_gid}/'
            .format(
                ent_gid=unicode(random_instance.entity_gid)),
            404)

        self.bad_delete_format_single(
            '/{ent_type}/'
            .format(
                ent_type=self.get_specific_key('ws_name')),
            405)

        self.bad_delete_format_single(
            '/{ent_type}'
            .format(
                ent_type=self.get_specific_key('ws_name')),
            301)

        self.bad_delete_format_single(
            '{ent_type}/{ent_gid}/'
            .format(
                ent_type=self.get_specific_key('ws_name'),
                ent_gid=unicode(random_instance.entity_gid)),
            401
        )

        self.bad_delete_format_single(
            '{ent_gid}'.format(
                ent_gid=unicode(random_instance.entity_gid)),
            404)

        self.bad_delete_format_single('/{ent_gid}/{ent_type}/'.format(
            ent_gid=unicode(random_instance.entity_gid),
            ent_type=self.get_specific_key('ws_name')), 404)

    def bad_delete_format_single(self, delete_uri, expected_http_status):
        instances_db = \
            db.session.query(self.get_specific_key('entity_class')).all()

        response_ws = self.client.delete(delete_uri, )
        self.assert_status(response_ws, expected_http_status)

        instances_db_after = \
            db.session.query(self.get_specific_key('entity_class')).all()
        self.assertTrue(len(instances_db), len(instances_db_after))
        for instance in instances_db_after:
            self.assertNotEquals(instance.master_revision.entity_data, None)

    def bad_delete_double_tests(self):
        instances_db = \
            db.session.query(self.get_specific_key('entity_class')).all()
        rand_pos = random.randint(0, len(instances_db) - 1)
        random_instance = instances_db[rand_pos]

        for i in range(4):
            response_ws = self.client.delete(
                '/{entity_type}/{entity_gid}/'.format(
                    entity_type=self.get_specific_key('ws_name'),
                    entity_gid=random_instance.entity_gid),
                headers=self.get_request_default_headers(),
                data="{\"revision\": {\"note\": \"A Test Note\"}}")

            if i == 0:
                self.assert200(response_ws)
            else:
                self.assert400(response_ws)
