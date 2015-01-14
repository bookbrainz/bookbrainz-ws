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


from bbschema import PublicationType
from flask.ext.restful import Resource, fields, marshal

from . import db, fields


class PublicationTypeResourceList(Resource):
    def get(self):
        types = db.session.query(PublicationType).all()

        return marshal({
            'count': len(types),
            'objects': types
        }, fields.publication_type_list)


def create_views(api):
    api.add_resource(PublicationTypeResourceList, '/publicationType')
