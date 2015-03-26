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


from bbschema import Gender, Language
from flask.ext.restful import Resource, marshal

from . import db, structures


class GenderResourceList(Resource):
    def get(self):
        genders = db.session.query(Gender).all()

        return marshal({
            'offset': 0,
            'objects': genders,
            'count': len(genders),
        }, structures.gender_list)


class LanguageResourceList(Resource):
    def get(self):
        languages = db.session.query(Language).all()

        return marshal({
            'offset': 0,
            'objects': languages,
            'count': len(languages),
        }, structures.language_list)


def create_views(api):
    api.add_resource(GenderResourceList, '/gender')
    api.add_resource(LanguageResourceList, '/language')
