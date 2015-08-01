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

from flask.ext.restful import Resource, abort, fields, marshal, reqparse

from bbschema import (CreatorData, EditionData, EntityRevision,
                      PublicationData, PublisherData, Revision, WorkData)
from sqlalchemy.orm.exc import NoResultFound

from . import db, structures

data_mapper = {
    PublicationData: structures.publication_diff,
    CreatorData: structures.creator_diff,
    EditionData: structures.edition_diff,
    PublisherData: structures.publisher_diff,
    WorkData: structures.work_diff,
}


def format_entity_revision(revision, base):
    entity_revision_fields = {
        'revision_id': fields.Integer,
        'created_at': fields.DateTime(dt_format='iso8601'),
        'entity': fields.Nested(structures.entity_stub),
        'user': fields.Nested({
            'user_id': fields.Integer,
        }),
        'uri': fields.Url('revision_get_single', True)
    }

    if base is None:
        right = revision.children
    else:
        try:
            right = [db.session.query(Revision).\
                filter_by(revision_id=base).one()]
        except NoResultFound:
            return marshal(revision, entity_revision_fields)

    if revision.entity_data is None:
        return marshal(revision, entity_revision_fields)

    changes = [revision.entity_data.diff(r.entity_data) for r in right]
    if not changes:
        changes = [revision.entity_data.diff(None)]
    data_fields = data_mapper[type(revision.entity_data)]

    entity_revision_fields['changes'] = \
            fields.List(fields.Nested(data_fields, allow_null=True))
    revision.changes = changes

    return marshal(revision, entity_revision_fields)

def format_relationship_revision(revision, base):
    relationship_revision_fields = {
        'revision_id': fields.Integer,
        'created_at': fields.DateTime(dt_format='iso8601'),
        'relationship': fields.Nested(structures.relationship_stub),
        'user': fields.Nested({
            'user_id': fields.Integer,
        }),
        'uri': fields.Url('revision_get_single', True)
    }

    if base is None:
        right = revision.children
    else:
        try:
            right = [db.session.query(Revision).\
                filter_by(revision_id=base).one()]
        except NoResultFound:
            return marshal(revision, relationship_revision_fields)

    if revision.relationship_data is None:
        return marshal(revision, relationship_revision_fields)

    changes = [revision.relationship_data.diff(r.relationship_data) for r in right]
    if not changes:
        changes = [revision.relationship_data.diff(None)]

    relationship_revision_fields['changes'] = \
            fields.List(fields.Nested(structures.relationship_diff, allow_null=True))
    revision.changes = changes

    return marshal(revision, relationship_revision_fields)

class RevisionResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('base', type=int, default=None)

    def get(self, revision_id):
        args = self.get_parser.parse_args()

        try:
            revision = db.session.query(Revision).\
                filter_by(revision_id=revision_id).one()
        except NoResultFound:
            abort(404)

        if isinstance(revision, EntityRevision):
            return format_entity_revision(revision, args.base)
        else:
            return format_relationship_revision(revision, args.base)


class RevisionResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('type', type=str)
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, entity_gid=None, user_id=None):
        args = self.get_parser.parse_args()
        query = db.session.query(Revision)

        if entity_gid is not None:
            query = db.session.query(EntityRevision)
            query = query.filter_by(entity_gid=entity_gid)
        elif user_id is not None:
            query = query.filter_by(user_id=user_id)

        list_fields = structures.revision_list

        if args.type == 'entity':
            query = query.filter_by(_type=1)
            list_fields = structures.entity_revision_list

        revisions = query.order_by(Revision.created_at.desc()).\
            offset(args.offset).limit(args.limit).all()

        return marshal({
            'offset': args.offset,
            'count': len(revisions),
            'objects': revisions
        }, list_fields)


def create_views(api):
    api.add_resource(RevisionResource, '/revision/<int:revision_id>/',
                     endpoint='revision_get_single')
    api.add_resource(
        RevisionResourceList, '/revision/', '/user/<int:user_id>/revisions',
        endpoint='revision_get_many'
    )
