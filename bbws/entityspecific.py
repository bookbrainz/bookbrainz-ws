from bbschema import CreatorData, Entity, EntityRevision, PublicationType
from flask.ext.restful import (abort, fields, marshal, marshal_with, reqparse,
                               Resource)
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import db

publication_type_list_fields = {
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'id': fields.Integer,
        'label': fields.String
    }))
}


class PublicationTypeResourceList(Resource):
    def get(self):
        types = db.session.query(PublicationType).all()

        return marshal({
            'count': len(types),
            'objects': types
        }, publication_type_list_fields)


def create_views(api):
    api.add_resource(PublicationTypeResourceList, '/publicationType')
