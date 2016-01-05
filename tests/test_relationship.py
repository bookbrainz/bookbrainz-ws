from bbws import create_app, db
from bbschema import Relationship, create_all
from flask_testing import TestCase
import datetime
from .fixture import load_data


class TestRelationshipViews(TestCase):
    def create_app(self):
        return create_app('../config/test.py')

    # noinspection PyPep8Naming
    def setUp(self):
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")
        db.engine.execute("CREATE SCHEMA bookbrainz")
        create_all(db.engine)
        load_data(db)

    def test_relationship_get_single(self):
        relationship_to_test = 1
        db_response = db.session.query(Relationship).filter(
            Relationship.relationship_id == relationship_to_test).one()
        rel_data = db_response.master_revision.relationship_data
        response = self.client.get('/relationship/' + str(relationship_to_test))
        self.assertEquals(response.json.get('relationship_id'),
                          relationship_to_test)
        self.assertEquals(
            response.json.get('uri'),
            'http://localhost/relationship/' + str(relationship_to_test))
        self.assertEquals(
            response.json.get('master_revision_id'),
            db_response.master_revision_id)
        self.assertTrue('last_updated' in response.json)
        self.assertEquals(len(response.json.get('entities', [])),
                          len(rel_data.entities))
        self.assertEquals(len(response.json.get('texts', [])),
                          len(rel_data.texts))

    def test_relationship_get_many(self):
        response = self.client.get('/relationship/', data={'limit': 100000})
        db_numer_of_relationships = len(db.session.query(Relationship).all())
        self.assertEquals(response.json.get('count'), db_numer_of_relationships)
        self.assertEquals(response.json.get('offset'), 0)
        self.assertEquals(len(response.json.get('objects', [])),
                          db_numer_of_relationships)
