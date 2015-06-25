# -*- coding: utf8 -*-

# Copyright (C) 2014-2015  Ben Ockmore

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

""" This module contains resources providing information from the MusicBrainz
schema.
"""


from flask.ext.restful import Resource, marshal, reqparse

from . import db, structures

from bbdata.model import Model, NotFoundError

Gender = Model('models/Gender.json')
Language = Model('models/Language.json')

class GenderResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        return Gender.list(db.session, args.offset,
                           args.limit, stub=(args.stub == 1))


class LanguageResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        all_languages = Language.list(db.session, args.offset,
                                      args.limit, stub=(args.stub == 1))
        return all_languages

def create_views(api):
    api.add_resource(GenderResourceList, '/gender/')
    api.add_resource(LanguageResourceList, '/language/')
