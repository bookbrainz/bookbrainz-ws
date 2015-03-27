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

from flask import request
from flask.ext.restful import Resource, abort, fields, marshal, reqparse

from bbschema import (CreatorData, EditionData, EntityRevision,
                      PublicationData, PublisherData, Revision, WorkData)
from sqlalchemy.orm.exc import NoResultFound

from . import db, oauth_provider, revision_json, structures

data_mapper = {
    PublicationData: ('publication_data', structures.publication_data),
    CreatorData: ('creator_data', structures.creator_data),
    EditionData: ('edition_data', structures.edition_data),
    PublisherData: ('publisher_data', structures.publisher_data),
    WorkData: ('work_data', structures.work_data),
}


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

        changes = revision_json.format_changes(args.base, revision.revision_id)

        data_fields = data_mapper.get(type(changes['data'][1]),
                                      data_mapper[PublicationData])
        entity_revision_fields = {
            'revision_id': fields.Integer,
            'created_at': fields.DateTime(dt_format='iso8601'),
            'entity': fields.Nested(structures.entity_stub),
            'user': fields.Nested({
                'user_id': fields.Integer,
            }),
            'uri': fields.Url('revision_get_single', True),
            'changes': fields.Nested({
                data_fields[0]: fields.List(fields.Nested(data_fields[1],
                                                          allow_null=True)),
                'annotation': fields.List(fields.String),
                'disambiguation': fields.List(fields.String),
                'aliases': fields.List(fields.Nested({
                    'name': fields.String,
                    'sort_name': fields.String,
                    'language_id': fields.Integer,
                }, allow_null=True)),
            })
        }

        changes[data_fields[0]] = changes['data']
        del changes['data']
        revision.changes = changes

        if isinstance(revision, EntityRevision):
            return marshal(revision, entity_revision_fields)
        else:
            return {
                'revision_id': revision.revision_id,
                'user_id': revision.user_id,
                'created_at': str(revision.created_at)
            }


class RevisionResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        args = self.get_parser.parse_args()
        query = db.session.query(Revision)

        revisions = query.offset(args.offset).limit(args.limit).all()
        return marshal({
            'offset': args.offset,
            'count': len(revisions),
            'objects': revisions
        }, structures.revision_list)


def create_views(api):
    api.add_resource(RevisionResource, '/revision/<int:revision_id>',
                     endpoint='revision_get_single')
    api.add_resource(RevisionResourceList, '/revisions',
                     endpoint='revision_get_many')
