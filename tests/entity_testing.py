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

import random

from bbschema import create_all
from werkzeug.test import Headers

from bbws import create_app, db
from get_bbid_testing import GetBBIDTests
from get_list_testing import GetListTests
from delete_testing import DeleteTests
from put_testing import PutTests
from post_testing import PostTests
from .fixture import load_data


class EntityTests(GetBBIDTests, GetListTests, DeleteTests, PutTests, PostTests):
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

    def put_data_check_specific(self, json_data, data_old, data_new):
        raise NotImplementedError

    def is_debug_mode(self):
        return True

    def get_specific_name(self, key):
        return self.specific_names[key]

    def get_request_default_headers(self):
        return self.request_default_headers


