from bbschema import EntityRevision, Revision, Edit
from flask.ext.restful import abort, fields, marshal_with, marshal, reqparse, Resource
from sqlalchemy.orm.exc import NoResultFound

from . import db


entity_revision_fields = {
    'id': fields.Integer,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'entity': fields.Nested({
        'gid': fields.String,
        'uri': fields.Url('entity_get_single', True)
    }),
    'user': fields.Nested({
        'id': fields.Integer,
    })
}


class RevisionResource(Resource):
    def get(self, id):
        try:
            revision = db.session.query(Revision).filter_by(id=id).one()
        except NoResultFound:
            abort(404)

        revision.uri = revision.id
        if isinstance(revision, EntityRevision):
            return marshal(revision, entity_revision_fields)
        else:
            return {
                'id': revision.id,
                'user_id': revision.user_id,
                'created_at': str(revision.created_at)
            }


revision_list_fields = {
    'objects': fields.List(fields.Nested({
        'id': fields.Integer,
        'uri': fields.Url('revision_get_single', True)
    }))
}


class RevisionResourceList(Resource):
    def get(self, edit_id=None):
        query = db.session.query(Revision)

        if edit_id is not None:
            query = query.join(Revision.edits).filter(Edit.id == edit_id)

        revisions = query.offset(0).limit(20).all()
        return marshal({
            'objects': revisions
        }, revision_list_fields)


def create_views(api):
    api.add_resource(RevisionResource, '/revision/<int:id>', endpoint='revision_get_single')
    api.add_resource(RevisionResourceList, '/revisions', '/edit/<int:edit_id>/revisions')
