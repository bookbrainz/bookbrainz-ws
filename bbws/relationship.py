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


""" This module contains the definitions for relationship and relationship-
related resources.
"""


from bbschema import (Relationship, RelationshipData, RelationshipEntity,
                      RelationshipRevision, RelationshipType)
from flask import request
from flask_restful import Resource, abort, fields, marshal, reqparse
from sqlalchemy.orm.exc import NoResultFound

from . import structures
from .services import db, oauth_provider


class RelationshipResource(Resource):
    def get(self, relationship_id):
        qry = db.session.query(Relationship).\
            filter_by(relationship_id=relationship_id)
        try:
            relationship = qry.one()
        except NoResultFound:
            abort(404)

        return marshal(relationship, structures.RELATIONSHIP)


class RelationshipResourceList(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, entity_gid=None):
        args = self.get_parser.parse_args()

        if entity_gid is not None:
            # Get the relationships for the specified entity.
            qry = db.session.query(Relationship).\
                join(RelationshipRevision, Relationship.master_revision).\
                join(RelationshipData).\
                join(RelationshipEntity).\
                filter(RelationshipEntity.entity_gid == entity_gid).\
                offset(args.offset).limit(args.limit)
        else:
            # Get all relationships.
            qry = db.session.query(Relationship).offset(
                args.offset
            ).limit(args.limit)

        relationships = qry.all()

        return marshal({
            'offset': args.offset,
            'count': len(relationships),
            'objects': relationships
        }, structures.RELATIONSHIP_LIST)

    @oauth_provider.require_oauth()
    def post(self):
        json = request.get_json()

        # This will be valid here, due to authentication.
        user = request.oauth.user
        user.total_revisions += 1
        user.revisions_applied += 1

        # Create a new relationship
        relationship = Relationship()
        # And some data to go in it
        relationship_data = RelationshipData.create(json)

        # Then, make the revision, passing relationship and data
        revision = RelationshipRevision(user_id=user.user_id)
        revision.relationship = relationship
        revision.relationship_data = relationship_data

        relationship.master_revision = revision

        db.session.add(revision)

        # Commit relationship, data and revision
        db.session.commit()

        return marshal(revision, {
            'relationship': fields.Nested(structures.RELATIONSHIP_STUB)
        })


class RelationshipTypeResource(Resource):

    def get(self, relationship_type_id):
        qry = db.session.query(RelationshipType).\
            filter_by(relationship_type_id=relationship_type_id)
        try:
            relationship_type = qry.one()
        except NoResultFound:
            abort(404)

        return marshal(relationship_type, structures.RELATIONSHIP_TYPE)


class RelationshipTypeResourceList(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        args = self.get_parser.parse_args()

        qry = db.session.query(RelationshipType).offset(args.offset)

        if args.limit is not None:
            qry = qry.limit(args.limit)

        types = qry.all()

        return marshal({
            'offset': args.offset,
            'count': len(types),
            'objects': types
        }, structures.RELATIONSHIP_TYPE_LIST)


def create_views(api):
    api.add_resource(
        RelationshipResource, '/relationship/<int:relationship_id>',
        endpoint='relationship_get_single'
    )
    api.add_resource(
        RelationshipResourceList, '/relationship/',
        '/entity/<string:entity_gid>/relationships/',
        endpoint='relationship_get_many'
    )
    api.add_resource(RelationshipTypeResource,
                     '/relationshipType/<int:relationship_type_id>')
    api.add_resource(RelationshipTypeResourceList, '/relationshipType/')
