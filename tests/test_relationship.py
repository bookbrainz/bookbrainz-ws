from bbws import create_app, db
from bbschema import Relationship, create_all
from flask.ext.testing import TestCase

import datetime

from .fixture import load_data


class TestRelationshipViews(TestCase):
    def create_app(self):
        return create_app('../config/test.py')

    def setUp(self):
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")
        db.engine.execute("CREATE SCHEMA bookbrainz")
        create_all(db.engine)
        load_data(db)

    def test_relationship_get_single(self):
        response = self.client.get('/relationship/3')
        self.assertEquals(response.json.get('relationship_id'), 3)
        self.assertEquals(response.json.get('uri'),
                          'http://localhost/relationship/3')
        self.assertEquals(response.json.get('master_revision_id'), 6)
        self.assertTrue('last_updated' in response.json)
        self.assertEquals(len(response.json.get('entities', [])), 1)
        self.assertEquals(len(response.json.get('texts', [])), 1)

    def test_relationship_get_many(self):
        response = self.client.get('/relationship/')
        self.assertEquals(response.json.get('count'), 3)
        self.assertEquals(response.json.get('offset'), 0)
        self.assertEquals(len(response.json.get('objects', [])), 3)
