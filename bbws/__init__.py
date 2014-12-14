
from flask import Flask
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask_redis import Redis
from flask_oauthlib.provider import OAuth2Provider

api = restful.Api()
db = SQLAlchemy()
cache = Redis()
oauth = OAuth2Provider()


def create_app(config_file):
    app = Flask(__name__.split('.')[0])
    app.config.from_pyfile(config_file)

    api.init_app(app)
    db.init_app(app)
    cache.init_app(app)
    oauth.init_app(app)

    import test
    import oauth as oauth_routes
    oauth_routes.init(app)
    test.init(app)

    return app
