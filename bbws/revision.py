from bbschema import Edit, EntityRevision, Revision
from flask.ext.restful import (abort, fields, marshal, marshal_with, reqparse,
                               Resource)
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.orm.exc import NoResultFound

from . import db
from .entity import entity_stub_fields

entity_revision_fields = {
    'id': fields.Integer,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'entity': fields.Nested(entity_stub_fields),
    'user': fields.Nested({
        'id': fields.Integer,
    }),
    'uri': fields.Url('revision_get_single', True)
}


class RevisionResource(Resource):
    def get(self, id):
        try:
            revision = db.session.query(Revision).filter_by(id=id).one()
        except NoResultFound:
            abort(404)

        if isinstance(revision, EntityRevision):
            return marshal(revision, entity_revision_fields)
        else:
            return {
                'id': revision.id,
                'user_id': revision.user_id,
                'created_at': str(revision.created_at)
            }


revision_list_fields = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(entity_revision_fields))
}


class RevisionResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, edit_id=None):
        args = self.get_parser.parse_args()
        query = db.session.query(Revision)

        if edit_id is not None:
            query = query.join(Revision.edits).filter(Edit.id == edit_id)

        revisions = query.offset(args.offset).limit(args.limit).all()
        return marshal({
            'offset': args.offset,
            'count': len(revisions),
            'objects': revisions
        }, revision_list_fields)

edit_fields = {
    'id': fields.Integer,
    'status': fields.Integer,
    'uri': fields.Url('edit_get_single', True)
}


class EditResource(Resource):
    def get(self, id):
        try:
            edit = db.session.query(Edit).filter_by(id=id).one()
        except NoResultFound:
            abort(404)

        return marshal(edit, edit_fields)

edit_list_fields = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(edit_fields))
}


class EditResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self, entity_gid=None, user_id=None):
        args = self.get_parser.parse_args()

        q = db.session.query(Edit)

        if entity_gid is not None:
            entity_revision_ = with_polymorphic(Revision, EntityRevision)
            q = q.join(Edit.revisions).join(EntityRevision).filter(
                EntityRevision.entity_gid == entity_gid
            )
        elif user_id is not None:
            q = q.filter_by(user_id=user_id)

        q = q.offset(args.offset).limit(args.limit)
        edits = q.all()

        return marshal({
            'offset': args.offset,
            'count': len(edits),
            'objects': edits
        }, edit_list_fields)


def create_views(api):
    api.add_resource(RevisionResource, '/revision/<int:id>', endpoint='revision_get_single')
    api.add_resource(RevisionResourceList, '/revisions', '/edit/<int:edit_id>/revisions')
    api.add_resource(EditResource, '/edit/<int:id>', endpoint='edit_get_single')
    api.add_resource(EditResourceList, '/edits', '/entity/<string:entity_gid>/edits', '/user/<int:user_id>/edits')
