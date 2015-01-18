from bbws import create_app, db
from bbschema import User, create_all
from flask.ext.testing import TestCase

import datetime

from .fixture import load_data


class TestUserViews(TestCase):
    def create_app(self):
        return create_app('../config/test.py')

    def setUp(self):
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")
        db.engine.execute("CREATE SCHEMA bookbrainz")
        create_all(db.engine)
        load_data(db)

    def tearDown(self):
        db.session.remove()
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")

    def test_user_get_single(self):
        # Create a User
        new_user = User(name=u'test_user1', email=u'test_user1@users.org', user_type_id=1)
        db.session.add(new_user)
        db.session.commit()

        created_at = new_user.created_at.replace(microsecond=0)
        active_at = new_user.active_at.replace(microsecond=0)

        response = self.client.get('/user/{}'.format(new_user.id))
        self.assertEquals(response.json, {
            u'name': new_user.name,
            u'reputation': new_user.reputation,
            u'bio': new_user.bio,
            u'created_at': datetime.datetime.isoformat(created_at),
            u'active_at': datetime.datetime.isoformat(active_at)
        })
