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

import uuid
from flask import request
from flask.ext.restful import Resource, abort, fields, marshal, reqparse

from bbschema import (Entity, EntityData, EntityRevision)
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import db, oauth_provider, structures


class EntityResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    entity_class = Entity
    entity_fields = structures.entity
    entity_data_fields = None

    def get(self, entity_gid):
        try:
            uuid.UUID(entity_gid)
        except ValueError:
            abort(404)

        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(self.entity_class).options(
                    joinedload('master_revision.entity_data')
                ).filter_by(entity_gid=entity_gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_data'),
                    joinedload('entity')
                ).filter_by(
                    revision_id=args.revision,
                    entity_gid=entity_gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            # No data, so 404
            abort(404)

        entity_data = revision.entity_data
        entity.revision = revision

        entity_out = marshal(entity, self.entity_fields)
        data_out = marshal(entity_data, self.entity_data_fields)

        entity_out.update(data_out)

        return entity_out


class EntityAliasResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, entity_gid):
        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_data.aliases')
                ).filter_by(entity_gid=entity_gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_data.aliases'),
                    joinedload('entity')
                ).filter_by(
                    revision_id=args.revision,
                    entity_gid=entity_gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            aliases = []
        else:
            aliases = revision.entity_data.aliases

        return marshal({
            'offset': 0,
            'count': len(aliases),
            'objects': aliases
        }, structures.entity_alias_list)


class EntityDisambiguationResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, entity_gid):
        try:
            uuid.UUID(entity_gid)
        except ValueError:
            abort(404)

        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_data.disambiguation')
                ).filter_by(entity_gid=entity_gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_data.disambiguation'),
                    joinedload('entity')
                ).filter_by(
                    revision_id=args.revision,
                    entity_gid=entity_gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            disambiguation = None
        else:
            disambiguation = revision.entity_data.disambiguation

        if disambiguation is None:
            return None
        else:
            return marshal(disambiguation, structures.entity_disambiguation)


class EntityAnnotationResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, entity_gid):
        try:
            uuid.UUID(entity_gid)
        except ValueError:
            abort(404)

        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_data.annotation')
                ).filter_by(entity_gid=entity_gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_data.annotation'),
                    joinedload('entity')
                ).filter_by(
                    revision_id=args.revision,
                    entity_gid=entity_gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None:
            annotation = None
        else:
            annotation = revision.entity_data.annotation

        if annotation is None:
            return None
        else:
            return marshal(annotation, structures.entity_annotation)


class EntityResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    entity_class = Entity
    entity_data_class = EntityData
    entity_stub_fields = structures.entity_stub
    entity_list_fields = structures.entity_list

    def get(self):
        args = self.get_parser.parse_args()
        q = db.session.query(self.entity_class).order_by(Entity.last_updated.desc())
        q = q.offset(args.offset).limit(args.limit)
        entities = q.all()

        return marshal({
            'offset': args.offset,
            'count': len(entities),
            'objects': entities
        }, self.entity_list_fields)

    @oauth_provider.require_oauth()
    def post(self):
        json = request.get_json()

        # This will be valid here, due to authentication.
        user = request.oauth.user

        entity = self.entity_class()
        entity_data = self.entity_data_class.create(json)

        revision = EntityRevision.create(user.user_id, entity, entity_data)

        entity.master_revision = revision

        db.session.add(revision)

        # Commit entity, data and revision
        db.session.commit()

        return marshal(revision, {
            'entity': fields.Nested(self.entity_stub_fields)
        })
