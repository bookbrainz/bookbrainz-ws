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


from flask.ext.restful import Resource, marshal

from bbschema import (CreatorType, EditionStatus, PublicationType,
                      PublisherType, WorkType)

from . import db, structures


class PublicationTypeResourceList(Resource):
    def get(self):
        types = db.session.query(PublicationType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.publication_type_list)


class CreatorTypeResourceList(Resource):
    def get(self):
        types = db.session.query(CreatorType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.creator_type_list)


class PublisherTypeResourceList(Resource):
    def get(self):
        types = db.session.query(PublisherType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.publisher_type_list)


class EditionStatusResourceList(Resource):
    def get(self):
        types = db.session.query(EditionStatus).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.edition_type_list)


class WorkTypeResourceList(Resource):
    def get(self):
        types = db.session.query(WorkType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.work_type_list)


def create_views(api):
    api.add_resource(PublicationTypeResourceList, '/publicationType/')
    api.add_resource(CreatorTypeResourceList, '/creatorType/')
    api.add_resource(PublisherTypeResourceList, '/publisherType/')
    api.add_resource(EditionStatusResourceList, '/editionStatus/')
    api.add_resource(WorkTypeResourceList, '/workType/')
