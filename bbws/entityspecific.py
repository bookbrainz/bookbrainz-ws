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


import uuid

from bbschema import (Publication)
from flask.ext.restful import Resource, marshal, reqparse
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import db, structures

from bbdata.model import Model, NotFoundError

PublicationType = Model('models/PublicationType.json')
PublisherType = Model('models/PublisherType.json')
CreatorType = Model('models/CreatorType.json')
EditionFormat = Model('models/EditionFormat.json')
EditionStatus = Model('models/EditionStatus.json')
WorkType = Model('models/WorkType.json')

class PublicationTypeResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        return PublicationType.list(db.session, args.offset,
                                    args.limit, stub=(args.stub == 1))

class CreatorTypeResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        return CreatorType.list(db.session, args.offset,
                                args.limit, stub=(args.stub == 1))


class PublisherTypeResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        return PublisherType.list(db.session, args.offset,
                                  args.limit, stub=(args.stub == 1))


class EditionFormatResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        return EditionFormat.list(db.session, args.offset,
                                  args.limit, stub=(args.stub == 1))


class EditionStatusResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        return EditionStatus.list(db.session, args.offset,
                                  args.limit, stub=(args.stub == 1))


class WorkTypeResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)
    get_parser.add_argument('stub', type=int, default=1)

    def get(self):
        args = self.get_parser.parse_args()
        return WorkType.list(db.session, args.offset,
                             args.limit, stub=(args.stub == 1))


class PublicationEditionsResource(Resource):
    def get(self, entity_gid):
        try:
            uuid.UUID(entity_gid)
        except ValueError:
            abort(404)

        try:
            publication = db.session.query(Publication).options(
                joinedload('master_revision.entity_data')
            ).filter_by(entity_gid=entity_gid).one()
        except NoResultFound:
            abort(404)

        return marshal({
            'offset': 0,
            'count': len(publication.editions),
            'objects': publication.editions
        }, structures.edition_list)


def create_views(api):
    api.add_resource(PublicationTypeResourceList, '/publicationType/')
    api.add_resource(CreatorTypeResourceList, '/creatorType/')
    api.add_resource(PublisherTypeResourceList, '/publisherType/')
    api.add_resource(EditionFormatResourceList, '/editionFormat/')
    api.add_resource(EditionStatusResourceList, '/editionStatus/')
    api.add_resource(WorkTypeResourceList, '/workType/')
    api.add_resource(
        PublicationEditionsResource, '/publication/<string:entity_gid>/editions',
        endpoint='publication_get_editions'
    )
