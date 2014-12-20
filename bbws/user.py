from bbschema import User
from flask.ext.restful import (abort, fields, marshal, marshal_with, reqparse,
                               Resource)
from sqlalchemy.orm.exc import NoResultFound

from . import db


user_fields = {
    'name': fields.String,
    'reputation': fields.Integer,
    'bio': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'active_at': fields.DateTime(dt_format='iso8601'),
}


class UserResource(Resource):
    def get(self, id):
        try:
            user = db.session.query(User).filter_by(id=id).one()
        except NoResultFound:
            about(404)

        return marshal(user, user_fields)

user_list_fields = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(user_fields))
}


class UserResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        args = self.get_parser.parse_args()
        users = db.session.query(User).offset(args.offset).limit(args.limit).all()

        return marshal({
            'offset': args.offset,
            'count': len(users),
            'objects': users
        }, user_list_fields)


def create_views(api):
    api.add_resource(UserResource, '/user/<int:id>',
                     endpoint='user_get_single')
    api.add_resource(UserResourceList, '/user', endpoint='user_get_many')
