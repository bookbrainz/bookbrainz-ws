from bbws import create_app, db
from bbschema import User, create_all
from flask.ext.testing import TestCase
from flask import url_for

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
        new_user = User(name=u'test_user1', password=b'', email=u'test_user1@users.org', user_type_id=1)
        db.session.add(new_user)
        db.session.commit()

        # TODO fix when flask restful releases next version
        import pytz
        from calendar import timegm
        created_at = datetime.datetime.isoformat(
            datetime.datetime.fromtimestamp(
                timegm(new_user.created_at.utctimetuple()), tz=pytz.UTC
            )
        )
        active_at = datetime.datetime.isoformat(
            datetime.datetime.fromtimestamp(
                timegm(new_user.active_at.utctimetuple()), tz=pytz.UTC
            )
        )

        response = self.client.get('/ws/user/{}/'.format(new_user.user_id))
        self.assertEquals(response.json.get(u'name'), new_user.name)
        self.assertEquals(response.json.get(u'reputation'),
                          new_user.reputation)
        self.assertEquals(response.json.get(u'bio'), new_user.bio)
        self.assertEquals(response.json.get(u'created_at'), created_at)
        self.assertEquals(response.json.get(u'active_at'), active_at)
        self.assertEquals(response.json.get(u'total_revisions'), 0)
        self.assertEquals(response.json.get(u'revisions_applied'), 0)
        self.assertEquals(response.json.get(u'revisions_reverted'), 0)
        self.assertEquals(response.json.get(u'user_type', {}), {
            'user_type_id': 1,
            'label': 'Editor'
        })
