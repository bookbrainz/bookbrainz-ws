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


import traceback

from bbschema import (Creator, CreatorData, Edition, EditionData, Entity,
                      EntityData, EntityRevision, IdentifierType, Publication,
                      PublicationData, Publisher, PublisherData, RevisionNote,
                      Work, WorkData)
from elasticsearch import Elasticsearch, ElasticsearchException
from flask import request
from flask_restful import Resource, abort, fields, marshal, reqparse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from bbws.revision import RevisionResourceList

from . import structures
from .services import db, oauth_provider
from .util import index_entity, is_uuid


class EntityResource(Resource):
    """ This class defines the generic methods for accessing Entity Resources.
    Derived classes should override the `entity_class`, `entity_fields`,
    `entity_data_fields` and `entity_stub_fields` class variables in order to
    allow the derived class to provide the expected endpoints.
    """

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    entity_class = None
    entity_fields = None
    entity_data_fields = None
    entity_stub_fields = None

    def get(self, entity_gid):
        if not is_uuid(entity_gid):
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
        if entity_data is not None:
            data_out = marshal(entity_data, self.entity_data_fields)
            entity_out.update(data_out)

        return entity_out

    @oauth_provider.require_oauth()
    def put(self, entity_gid):
        data = request.get_json()

        # This will be valid here, due to authentication.
        user = request.oauth.user
        user.total_revisions += 1
        user.revisions_applied += 1

        if not is_uuid(entity_gid):
            abort(404)

        try:
            entity = db.session.query(self.entity_class).options(
                joinedload('master_revision.entity_data')
            ).filter_by(entity_gid=entity_gid).one()
        except NoResultFound:
            abort(404)

        if entity.master_revision is None:
            abort(403)  # Forbidden to PUT on an entity with no data yet

        entity_data = entity.master_revision.entity_data
        entity_data = entity_data.update(data, db.session)

        revision = EntityRevision(user_id=user.user_id)
        revision.entity = entity
        revision.entity_data = entity_data

        note_content = data.get('revision', {}).get('note', '')

        if note_content != '':
            note = RevisionNote(user_id=user.user_id,
                                revision_id=revision.revision_id,
                                content=data['revision']['note'])

            revision.notes.append(note)

        entity.master_revision.parent = revision
        entity.master_revision = revision

        db.session.add(revision)

        # Commit entity, data and revision
        db.session.commit()

        entity_out = marshal(revision.entity, self.entity_fields)
        data_out = marshal(revision.entity_data, self.entity_data_fields)

        entity_out.update(data_out)

        # Don't 500 if we fail to index; commit still succeeded
        try:
            es_conn = Elasticsearch()
            index_entity(es_conn, entity_out)
        except ElasticsearchException:
            pass

        return marshal(revision, {
            'entity': fields.Nested(self.entity_stub_fields)
        })

    @oauth_provider.require_oauth()
    def delete(self, entity_gid):
        data = request.get_json()

        # This will be valid here, due to authentication.
        user = request.oauth.user
        user.total_revisions += 1
        user.revisions_applied += 1

        if not is_uuid(entity_gid):
            abort(404)

        try:
            entity = db.session.query(self.entity_class).options(
                joinedload('master_revision')
            ).filter_by(entity_gid=entity_gid).one()
        except NoResultFound:
            abort(404)

        if entity.master_revision is None:
            abort(403)  # Forbidden to DELETE an entity with no data yet

        # To delete an entity, create a new revision with entity_data set to
        # None
        revision = EntityRevision(user_id=user.user_id)
        revision.entity = entity
        revision.entity_data = None

        note_content = data.get('revision', {}).get('note', '')

        if note_content != '':
            note = RevisionNote(user_id=user.user_id,
                                revision_id=revision.revision_id,
                                content=data['revision']['note'])

            revision.notes.append(note)

        entity.master_revision.parent = revision
        entity.master_revision = revision

        db.session.add(revision)

        # Commit entity, data and revision
        db.session.commit()

        return marshal(revision, {
            'entity': fields.Nested(self.entity_stub_fields)
        })


class EntityAliasResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, entity_gid):
        if not is_uuid(entity_gid):
            abort(404)

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

        if revision is None or revision.entity_data is None:
            aliases = []
        else:
            aliases = revision.entity_data.aliases

        return marshal({
            'offset': 0,
            'count': len(aliases),
            'objects': aliases
        }, structures.ENTITY_ALIAS_LIST)


class EntityDisambiguationResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, entity_gid):
        if not is_uuid(entity_gid):
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

        if revision is None or revision.entity_data is None:
            disambiguation = None
        else:
            disambiguation = revision.entity_data.disambiguation

        if disambiguation is None:
            return None
        else:
            return marshal(disambiguation, structures.ENTITY_DISAMBIGUATION)


class EntityAnnotationResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, entity_gid):
        if not is_uuid(entity_gid):
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

        if revision is None or revision.entity_data is None:
            annotation = None
        else:
            annotation = revision.entity_data.annotation

        if annotation is None:
            return None
        else:
            return marshal(annotation, structures.ENTITY_ANNOTATION)


class EntityIdentifierResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('revision', type=int, default=None)

    def get(self, entity_gid):
        args = self.get_parser.parse_args()
        if args.revision is None:
            try:
                entity = db.session.query(Entity).options(
                    joinedload('master_revision.entity_data.identifiers')
                ).filter_by(entity_gid=entity_gid).one()
            except NoResultFound:
                abort(404)
            else:
                revision = entity.master_revision
        else:
            try:
                revision = db.session.query(EntityRevision).options(
                    joinedload('entity_data.identifiers'),
                    joinedload('entity')
                ).filter_by(
                    revision_id=args.revision,
                    entity_gid=entity_gid
                ).one()
            except NoResultFound:
                abort(404)
            else:
                entity = revision.entity

        if revision is None or revision.entity_data is None:
            identifiers = []
        else:
            identifiers = revision.entity_data.identifiers

        return marshal({
            'offset': 0,
            'count': len(identifiers),
            'objects': identifiers
        }, structures.IDENTIFIER_LIST)


class EntityIdentifierTypeResourceList(Resource):
    def get(self):
        types = db.session.query(IdentifierType).all()

        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.IDENTIFIER_TYPE_LIST)


class EntityResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    entity_class = None
    entity_data_class = None
    entity_stub_fields = None
    entity_data_fields = None
    entity_list_fields = None

    def get(self):
        args = self.get_parser.parse_args()
        query = db.session.query(self.entity_class).\
            order_by(Entity.last_updated.desc())
        query = query.offset(args.offset).limit(args.limit)
        entities = query.all()

        return marshal({
            'offset': args.offset,
            'count': len(entities),
            'objects': entities
        }, self.entity_list_fields)

    @oauth_provider.require_oauth()
    def post(self):
        data = request.get_json()

        # This will be valid here, due to authentication.
        user = request.oauth.user
        user.total_revisions += 1
        user.revisions_applied += 1

        entity = self.entity_class()
        entity_data = self.entity_data_class.create(data, db.session)

        revision = EntityRevision(user_id=user.user_id)
        revision.entity = entity
        revision.entity_data = entity_data

        note_content = data.get('revision', {}).get('note', '')

        if note_content != '':
            note = RevisionNote(user_id=user.user_id,
                                revision_id=revision.revision_id,
                                content=data['revision']['note'])

            revision.notes.append(note)

        entity.master_revision = revision

        db.session.add(revision)

        # Commit entity, data and revision
        try:
            db.session.commit()
        except IntegrityError:
            # There was an issue with the data we received, so 400
            print traceback.format_exc()
            abort(400)

        entity_out = marshal(revision.entity, structures.ENTITY_EXPANDED)
        data_out = marshal(revision.entity_data, self.entity_data_fields)

        entity_out.update(data_out)

        # Don't 500 if we fail to index; commit still succeeded
        try:
            es_conn = Elasticsearch()
            index_entity(es_conn, entity_out)
        except ElasticsearchException:
            pass

        return marshal(revision, {
            'entity': fields.Nested(self.entity_stub_fields)
        })


def make_entity_endpoints(api, entity_class, data_class, make_list=True):

    entity_name = entity_class.__name__.lower()
    entity_name_upper = entity_name.upper()
    entity_struct = getattr(structures, entity_name_upper)
    stub_struct = getattr(structures, entity_name_upper + '_STUB')
    data_struct = getattr(structures, entity_name_upper + '_DATA')
    list_struct = getattr(structures, entity_name_upper + '_LIST')

    resource_class = type(
        entity_class.__name__ + 'Resource', (EntityResource,),
        {
            'entity_class': entity_class,
            'entity_fields': entity_struct,
            'entity_data_fields': data_struct,
            'entity_stub_fields': stub_struct
        }
    )

    api.add_resource(
        resource_class, '/{}/<string:entity_gid>/'.format(entity_name),
        endpoint='{}_get_single'.format(entity_name)
    )

    api.add_resource(
        EntityAliasResource,
        '/{}/<string:entity_gid>/aliases'.format(entity_name),
        endpoint='{}_get_aliases'.format(entity_name)
    )

    api.add_resource(
        EntityDisambiguationResource,
        '/{}/<string:entity_gid>/disambiguation'.format(entity_name),
        endpoint='{}_get_disambiguation'.format(entity_name)
    )

    api.add_resource(
        EntityAnnotationResource,
        '/{}/<string:entity_gid>/annotation'.format(entity_name),
        endpoint='{}_get_annotation'.format(entity_name)
    )

    api.add_resource(
        EntityIdentifierResource,
        '/{}/<string:entity_gid>/identifiers'.format(entity_name),
        endpoint='{}_get_identifiers'.format(entity_name))

    api.add_resource(
        RevisionResourceList,
        '/{}/<string:entity_gid>/revisions'.format(entity_name),
        endpoint='{}_get_revisions'.format(entity_name))

    if make_list:
        list_class = type(
            entity_class.__name__ + 'List', (EntityResourceList,),
            {
                'entity_class': entity_class,
                'entity_data_class': data_class,
                'entity_fields': entity_struct,
                'entity_data_fields': data_struct,
                'entity_stub_fields': stub_struct,
                'entity_list_fields': list_struct
            }
        )

        api.add_resource(list_class, '/{}/'.format(entity_name))


def create_views(api):
    make_entity_endpoints(api, Entity, EntityData, make_list=False)
    make_entity_endpoints(api, Edition, EditionData)
    make_entity_endpoints(api, Work, WorkData)
    make_entity_endpoints(api, Publication, PublicationData)
    make_entity_endpoints(api, Publisher, PublisherData)
    make_entity_endpoints(api, Creator, CreatorData)

    api.add_resource(
        EntityIdentifierTypeResourceList,
        '/identifierType/'
    )
