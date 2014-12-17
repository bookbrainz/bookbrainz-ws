from flask.ext.restful import Resource, reqparse, abort
from sqlalchemy.orm.exc import NoResultFound

from . import db

from bbschema import Entity

class EntityResource(Resource):
    def get(self, gid):
        try:
            entity = db.session.query(Entity).filter_by(gid=gid).one()
        except NoResultFound:
            abort(404)

        return {
            'gid': str(entity.gid),
            'master_revision_id': entity.master_revision_id,
            'last_updated': str(entity.last_updated)
        }

class EntityResourceList(Resource):
    def get(self):
        entities = db.session.query(Entity).offset(0).limit(20).all()
        return {
            "objects": [
                {
                    'gid': str(entity.gid),
                    'master_revision_id': entity.master_revision_id,
                    'last_updated': str(entity.last_updated)
                }
            for entity in entities]
        }


def create_views(api):
    api.add_resource(EntityResource, '/entity/<string:gid>', endpoint='entity_get_single')
    api.add_resource(EntityResourceList, '/entity')
