import datetime
import json

from flask import url_for
from flask_testing import TestCase

from bbschema import User, create_all
from bbws import create_app, db

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
        user = db.session.query(User).get(1)

        # TODO fix when flask restful releases next version
        import pytz
        from calendar import timegm
        created_at = user.created_at.isoformat()
        active_at = user.active_at.isoformat()

        response = self.client.get('/user/{}/'.format(user.user_id))
        self.assert200(response)
        self.assertEquals(response.json.get(u'name'), user.name)
        self.assertEquals(response.json.get(u'reputation'),
                          user.reputation)
        self.assertEquals(response.json.get(u'bio'), user.bio)
        self.assertEquals(response.json.get(u'created_at'), created_at)
        self.assertEquals(response.json.get(u'active_at'), active_at)
        self.assertEquals(response.json.get(u'total_revisions'), 0)
        self.assertEquals(response.json.get(u'revisions_applied'), 0)
        self.assertEquals(response.json.get(u'revisions_reverted'), 0)
        self.assertEquals(response.json.get(u'user_type', {}), {
            'user_type_id': user.user_type.user_type_id,
            'label': 'Editor'
        })

    def test_user_get_single_bad_numeric_id(self):
        response = self.client.get('/user/9999/')
        self.assert404(response)

    def test_user_get_single_bad_string_id(self):
        response = self.client.get('/user/abc/')
        self.assert404(response)

    def test_user_get_many(self):
        response = self.client.get('/user/')
        self.assert200(response)

        self.assertTrue(isinstance(response.json.get(u'objects'), list))

        self.assertTrue(response.json.get(u'objects'))
        self.assertEquals(response.json[u'objects'][0].get('user_id'), 1)
        self.assertTrue('bio' in response.json[u'objects'][0])
        self.assertTrue('created_at' in response.json[u'objects'][0])
        self.assertTrue('active_at' in response.json[u'objects'][0])
        self.assertTrue('total_revisions' in response.json[u'objects'][0])
        self.assertTrue('revisions_applied' in response.json[u'objects'][0])
        self.assertTrue('revisions_reverted' in response.json[u'objects'][0])
        self.assertTrue('user_type' in response.json[u'objects'][0])
        self.assertTrue('reputation' in response.json[u'objects'][0])

    def test_user_post(self):
        headers = [('Content-Type', 'application/json')]
        payload = {'name': 'ABC', 'email': 'DEF@GHI.JKL', 'password': 'MNO',
                   'user_type': {'user_type_id': 1}}
        response = self.client.post('/user/', headers=headers,
                                    data=json.dumps(payload))

        self.assert200(response)
        self.assertTrue(isinstance(response.json.get(u'user_id'), (int, long)))
        self.assertEquals(response.json.get(u'name'), 'ABC')
        self.assertEquals(response.json.get(u'bio'), None)
        self.assertEquals(response.json.get(u'total_revisions'), 0)
        self.assertEquals(response.json.get(u'revisions_applied'), 0)
        self.assertEquals(response.json.get(u'revisions_reverted'), 0)

        # And check private attributes
        user = db.session.query(User).get(response.json[u'user_id'])
        self.assertEquals(user.email, 'DEF@GHI.JKL')
        self.assertTrue(user.password)

    def test_user_post_missing_name(self):
        headers = [('Content-Type', 'application/json')]
        payload = {'email': 'DEF@GHI.JKL', 'password': 'MNO',
                   'user_type': {'user_type_id': 1}}
        response = self.client.post('/user/', headers=headers,
                                    data=json.dumps(payload))

        self.assert400(response)

    def test_user_post_missing_email(self):
        headers = [('Content-Type', 'application/json')]
        payload = {'name': 'ABC', 'password': 'MNO',
                   'user_type': {'user_type_id': 1}}
        response = self.client.post('/user/', headers=headers,
                                    data=json.dumps(payload))

        self.assert400(response)

    def test_user_post_missing_password(self):
        headers = [('Content-Type', 'application/json')]
        payload = {'name': 'ABC', 'email': 'DEF@GHI.JKL',
                   'user_type': {'user_type_id': 1}}
        response = self.client.post('/user/', headers=headers,
                                    data=json.dumps(payload))

        self.assert400(response)

    def test_user_post_missing_type(self):
        headers = [('Content-Type', 'application/json')]
        payload = {'name': 'ABC', 'email': 'DEF@GHI.JKL', 'password': 'MNO'}
        response = self.client.post('/user/', headers=headers,
                                    data=json.dumps(payload))

        self.assert400(response)
