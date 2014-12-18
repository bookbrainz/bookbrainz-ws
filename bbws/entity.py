from bbschema import CreatorData, Entity, PublicationData
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

    def get(self, gid):
        try:
            entity = db.session.query(Entity).options(
                joinedload('master_revision.entity_tree.aliases')
            ).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        if entity.master_revision is None:
            alises = []
        else:
            aliases = entity.master_revision.entity_tree.aliases

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
    def get(self, gid):
        try:
            entity = db.session.query(Entity).options(
                joinedload('master_revision.entity_tree.disambiguation')
            ).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        if entity.master_revision is None:
            disambiguation = None
        else:
            disambiguation = entity.master_revision.entity_tree.disambiguation

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
    def get(self, gid):
        try:
            entity = db.session.query(Entity).options(
                joinedload('master_revision.entity_tree.annotation')
            ).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        if entity.master_revision is None:
            annotation = None
        else:
            annotation = entity.master_revision.entity_tree.annotation

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
    PublicationData: publication_data_fields,
    CreatorData: creator_data_fields
}


class EntityDataResource(Resource):
    def get(self, gid):
        try:
            entity = db.session.query(Entity).options(
                joinedload('master_revision.entity_tree.data')
            ).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        if entity.master_revision is None:
            data = None
        else:
            data = entity.master_revision.entity_tree.data

        data_fields = data_mapper.get(type(data), data_mapper[PublicationData])

        entity_data_fields = {
            'entity': fields.Nested(entity_stub_fields),
            'data': fields.Nested(data_fields, allow_null=True)
        }

        return marshal({
            'entity': entity,
            'data': data
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
