from flask.ext.restful import Resource, fields, marshal_with, marshal, reqparse, abort
from sqlalchemy.orm.exc import NoResultFound

from . import db

from bbschema import Entity

entity_stub_fields = {
    'gid': fields.String,
    'uri': fields.Url('entity_get_single', True)
}

entity_fields = {
    'gid': fields.String,
    'master_revision_id': fields.Integer,
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'uri': fields.Url('entity_get_single', True),
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
        'label': fields.String
    }))
}

class EntityAliasResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, gid):
        args = self.get_parser.parse_args()
        try:
            entity = db.session.query(Entity).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        # This is a lot of queries. Either use eager loading, or find some other
        # way of reducing queries here.
        return marshal({
            'entity': entity,
            'aliases': entity.master_revision.entity_tree.aliases
        }, entity_alias_fields)


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
    api.add_resource(EntityResource, '/entity/<string:gid>', endpoint='entity_get_single')
    api.add_resource(EntityAliasResource, '/entity/<string:gid>/aliases', endpoint='entity_get_aliases')
    api.add_resource(EntityResourceList, '/entity')
