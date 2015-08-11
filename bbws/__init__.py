# -*- coding: utf8 -*-

# Copyright (C) 2014-2015  Ben Ockmore

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


""" This module provides the function for creating an instance of the
webservice application, importing other modules to add routes.
"""


from flask import Flask
from flask_restful import Api

from .services import db, cache, oauth_provider
from .util import add_cors_header


def create_app(config_file):
    """ Create the webservice application using the configuration provided in
    config_file, and initialize SQLAlchemy, Redis and OAuth services. Also
    installs webservice routes.
    """

    app = Flask(__name__.split('.')[0])
    app.config.from_pyfile(config_file)
    app.after_request(add_cors_header)

    # Initialize Flask extensions
    api = Api(app)
    db.init_app(app)
    cache.init_app(app)
    oauth_provider.init_app(app)

    # Initialize OAuth handler
    import bbws.oauth
    bbws.oauth.init(app)

    # Initialize custom endpoints
    import bbws.custom
    bbws.custom.init(app)

    # Initialize webservice routes
    import bbws.entity
    import bbws.revision
    import bbws.user
    import bbws.entityspecific
    import bbws.relationship
    import bbws.musicbrainz

    bbws.entity.create_views(api)
    bbws.revision.create_views(api)
    bbws.user.create_views(api)
    bbws.entityspecific.create_views(api)
    bbws.relationship.create_views(api)
    bbws.musicbrainz.create_views(api)

    return app
