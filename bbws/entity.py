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


""" This module contains the definitions for generic entity and entity-related
resources.
"""


from bbschema import CreatorData, Entity, EntityRevision, PublicationData
from flask.ext.restful import Resource, abort, fields, marshal, reqparse
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import db, structures


class EntityResource(Resource):
    def get(self, gid):
        try:
            entity = db.session.query(Entity).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        return marshal(entity, structures.entity)


class EntityAliasResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, gid):
        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_tree.aliases')
                ).filter_by(gid=gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_tree.aliases'),
                    joinedload('entity')
                ).filter_by(
                    id=args.revision,
                    entity_gid=gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            aliases = []
        else:
            aliases = revision.entity_tree.aliases

        return marshal({
            'entity': entity,
            'aliases': aliases
        }, structures.entity_alias)


class EntityDisambiguationResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, gid):
        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_tree.disambiguation')
                ).filter_by(gid=gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_tree.disambiguation'),
                    joinedload('entity')
                ).filter_by(
                    id=args.revision,
                    entity_gid=gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            disambiguation = None
        else:
            disambiguation = revision.entity_tree.disambiguation

        return marshal({
            'entity': entity,
            'disambiguation': disambiguation
        }, structures.entity_disambiguation)


class EntityAnnotationResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, gid):
        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_tree.annotation')
                ).filter_by(gid=gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_tree.annotation'),
                    joinedload('entity')
                ).filter_by(
                    id=args.revision,
                    entity_gid=gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            annotation = None
        else:
            annotation = revision.entity_tree.annotation

        return marshal({
            'entity': entity,
            'annotation': annotation
        }, structures.entity_annotation)


data_mapper = {
    PublicationData: ('publication_data', structures.publication_data),
    CreatorData: ('creator_data', structures.creator_data)
}


class EntityDataResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, gid):
        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_tree.data')
                ).filter_by(gid=gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_tree.data'),
                    joinedload('entity')
                ).filter_by(
                    id=args.revision,
                    entity_gid=gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            # No data, so 404
            abort(404)
        else:
            data = revision.entity_tree.data

        data_fields = data_mapper[type(data)]

        entity_data_fields = {
            'entity': fields.Nested(structures.entity_stub),
            data_fields[0]: fields.Nested(data_fields[1], allow_null=True)
        }

        return marshal({
            'entity': entity,
            data_fields[0]: data
        }, entity_data_fields)


class EntityResourceList(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        args = self.get_parser.parse_args()
        q = db.session.query(Entity).offset(args.offset).limit(args.limit)
        entities = q.all()
        return marshal({
            'offset': args.offset,
            'count': len(entities),
            'objects': entities
        }, structures.entity_list)


def create_views(api):
    api.add_resource(EntityResource, '/entity/<string:gid>',
                     endpoint='entity_get_single')
    api.add_resource(EntityAliasResource, '/entity/<string:gid>/aliases',
                     endpoint='entity_get_aliases')
    api.add_resource(
        EntityDisambiguationResource, '/entity/<string:gid>/disambiguation',
        endpoint='entity_get_disambiguation'
    )
    api.add_resource(
        EntityAnnotationResource, '/entity/<string:gid>/annotation',
        endpoint='entity_get_annotation'
    )
    api.add_resource(EntityDataResource, '/entity/<string:gid>/data',
                     endpoint='entity_get_data')
    api.add_resource(EntityResourceList, '/entity')
