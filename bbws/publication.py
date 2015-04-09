# -*- coding: utf8 -*-

# Copyright (C) 2015 Sean Burke

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


""" This module contains the definitions for generic entity and entity-related
resources.
"""

import uuid

from flask.ext.restful import Resource, marshal

from bbschema import Publication, PublicationData, Edition, EditionData
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import db, structures
from .entity import (EntityAliasResource, EntityAnnotationResource,
                     EntityDisambiguationResource, EntityResource,
                     EntityResourceList)


class PublicationResource(EntityResource):
    entity_class = Publication
    entity_fields = structures.publication
    entity_data_fields = structures.publication_data


class PublicationEditionsResource(Resource):
    def get(self, entity_gid):
        try:
            uuid.UUID(entity_gid)
        except ValueError:
            abort(404)

        try:
            editions = db.session.query(Edition).options(
                joinedload('master_revision.entity_data')
            ).filter(EditionData.publication_gid == entity_gid).all()
        except NoResultFound:
            abort(404)

        return marshal({
            'offset': 0,
            'count': len(editions),
            'objects': editions
        }, structures.edition_list)


class PublicationResourceList(EntityResourceList):
    entity_class = Publication
    entity_data_class = PublicationData
    entity_data_fields = structures.publication_data
    entity_stub_fields = structures.publication_stub
    entity_list_fields = structures.publication_list


def create_views(api):
    api.add_resource(PublicationResource, '/publication/<string:entity_gid>/',
                     endpoint='publication_get_single')

    api.add_resource(
        EntityAliasResource, '/publication/<string:entity_gid>/aliases',
        endpoint='publication_get_aliases'
    )

    api.add_resource(
        EntityDisambiguationResource,
        '/publication/<string:entity_gid>/disambiguation',
        endpoint='publication_get_disambiguation'
    )

    api.add_resource(
        EntityAnnotationResource, '/publication/<string:entity_gid>/annotation',
        endpoint='publication_get_annotation'
    )

    api.add_resource(
        PublicationEditionsResource, '/publication/<string:entity_gid>/editions',
        endpoint='publication_get_editions'
    )

    api.add_resource(PublicationResourceList, '/publication/')
