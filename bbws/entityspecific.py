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


from bbschema import (CreatorType, EditionFormat, EditionStatus, Publication,
                      PublicationType, Publisher, PublisherType, WorkType)
from flask_restful import Resource, abort, marshal
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import structures
from .services import db
from .util import is_uuid


class PublicationTypeResourceList(Resource):
    def get(self):
        types = db.session.query(PublicationType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.PUBLICATION_TYPE_LIST)


class CreatorTypeResourceList(Resource):
    def get(self):
        types = db.session.query(CreatorType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.CREATOR_TYPE_LIST)


class PublisherTypeResourceList(Resource):
    def get(self):
        types = db.session.query(PublisherType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.PUBLISHER_TYPE_LIST)


class EditionFormatResourceList(Resource):
    def get(self):
        types = db.session.query(EditionFormat).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.EDITION_FORMAT_LIST)


class EditionStatusResourceList(Resource):
    def get(self):
        types = db.session.query(EditionStatus).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.EDITION_STATUS_ID)


class WorkTypeResourceList(Resource):
    def get(self):
        types = db.session.query(WorkType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.WORK_TYPE_LIST)


class PublicationEditionsResource(Resource):
    def get(self, entity_gid):
        if not is_uuid(entity_gid):
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
        }, structures.EDITION_LIST)


class PublisherEditionsResource(Resource):
    def get(self, entity_gid):
        if not is_uuid(entity_gid):
            abort(404)

        try:
            publisher = db.session.query(Publisher).options(
                joinedload('master_revision.entity_data')
            ).filter_by(entity_gid=entity_gid).one()
        except NoResultFound:
            abort(404)

        return marshal({
            'offset': 0,
            'count': len(publisher.editions),
            'objects': publisher.editions
        }, structures.EDITION_LIST)


def create_views(api):
    api.add_resource(PublicationTypeResourceList, '/publicationType/')
    api.add_resource(CreatorTypeResourceList, '/creatorType/')
    api.add_resource(PublisherTypeResourceList, '/publisherType/')
    api.add_resource(EditionFormatResourceList, '/editionFormat/')
    api.add_resource(EditionStatusResourceList, '/editionStatus/')
    api.add_resource(WorkTypeResourceList, '/workType/')
    api.add_resource(
        PublicationEditionsResource,
        '/publication/<string:entity_gid>/editions',
        endpoint='publication_get_editions'
    )
    api.add_resource(
        PublisherEditionsResource, '/publisher/<string:entity_gid>/editions',
        endpoint='publisher_get_editions'
    )
