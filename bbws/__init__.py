
from flask import Flask
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask_redis import Redis
from flask_oauthlib.provider import OAuth2Provider

db = SQLAlchemy()
cache = Redis()
oauth_provider = OAuth2Provider()


def add_cors_header(response):
    # https://github.com/jfinkels/flask-restless/issues/223
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
        'HEAD, GET, POST, PATCH, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response


def create_app(config_file):
    app = Flask(__name__.split('.')[0])
    app.config.from_pyfile(config_file)
    app.after_request(add_cors_header)

    api = restful.Api(app)
    db.init_app(app)
    cache.init_app(app)
    oauth_provider.init_app(app)

    import test
    import oauth as oauth_routes
    oauth_routes.init(app)
    test.init(app)

    return app
