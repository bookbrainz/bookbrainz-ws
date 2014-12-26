from bbschema import CreatorData, Entity, PublicationData, EntityRevision
from flask.ext.restful import (abort, fields, marshal, marshal_with, reqparse,
                               Resource)
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import db

entity_stub_fields = {
    'gid': fields.String,
    'uri': fields.Url('entity_get_single', True)
}

entity_fields = {
    u'gid': fields.String,
    u'master_revision_id': fields.Integer,
    u'last_updated': fields.DateTime(dt_format='iso8601'),
    u'uri': fields.Url('entity_get_single', True),
    u'aliases_uri': fields.Url('entity_get_aliases', True),
    u'disambiguation_uri': fields.Url('entity_get_disambiguation', True),
    u'annotation_uri': fields.Url('entity_get_annotation', True),
    u'data_uri': fields.Url('entity_get_data', True)
}


class EntityResource(Resource):
    def get(self, gid):
        try:
            entity = db.session.query(Entity).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        return marshal(entity, entity_fields)

entity_alias_fields = {
    'entity': fields.Nested(entity_stub_fields),
    'aliases': fields.List(fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
        'sort_name': fields.String
    }))
}


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
            alises = []
        else:
            aliases = revision.entity_tree.aliases

        return marshal({
            'entity': entity,
            'aliases': aliases
        }, entity_alias_fields)

entity_disambiguation_fields = {
    'entity': fields.Nested(entity_stub_fields),
    'disambiguation': fields.Nested({
        'id': fields.Integer(),
        'comment': fields.String()
    }, allow_null=True)
}


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
        }, entity_disambiguation_fields)


entity_annotation_fields = {
    'entity': fields.Nested(entity_stub_fields),
    'annotation': fields.Nested({
        'id': fields.Integer(),
        'created_at': fields.DateTime(dt_format='iso8601'),
        'content': fields.String()
    }, allow_null=True)
}


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
        }, entity_annotation_fields)

publication_data_fields = {
    'id': fields.Integer,
    'publication_type': fields.Nested({
        'id': fields.Integer,
        'label': fields.String
    })
}

creator_data_fields = {
    'id': fields.Integer,
    'begin_date': fields.DateTime(dt_format='iso8601'),
    'begin_date_precision': fields.String,
    'end_date': fields.DateTime(dt_format='iso8601'),
    'end_date_precision': fields.String,
    'ended': fields.Boolean,
    'creator_type': fields.Nested({
        'id': fields.Integer,
        'label': fields.String
    })
}

data_mapper = {
    PublicationData: ('publication_data', publication_data_fields),
    CreatorData: ('creator_data', creator_data_fields)
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
            data = None
        else:
            data = revision.entity_tree.data

        data_fields = data_mapper.get(type(data), data_mapper[PublicationData])

        entity_data_fields = {
            'entity': fields.Nested(entity_stub_fields),
            data_fields[0]: fields.Nested(data_fields[1], allow_null=True)
        }

        return marshal({
            'entity': entity,
            data_fields[0]: data
        }, entity_data_fields)


entity_list_fields = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(entity_fields))
}


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
        }, entity_list_fields)


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
