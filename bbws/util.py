# -*- coding: utf8 -*-

# Copyright (C) 2015  Ben Ockmore

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


import uuid


def is_uuid(test_str):
    """ Tests whether the input is a valid UUID and returns True if it is, false
    otherwise.
    """
    try:
        uuid.UUID(test_str)
    except ValueError:
        return False
    else:
        return True


def index_entity(es_conn, entity):
    """ Index an entity in the provided elasticsearch connection. """
    es_conn.index(
        index='bookbrainz',
        doc_type=entity['_type'].lower(),
        id=entity['entity_gid'],
        body=entity
    )


def add_cors_header(response):
    """ Adds CORS headers to responses, so that cross-domain requests are
    responded to successfully - see
    https://github.com/jfinkels/flask-restless/issues/223
    """

    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = \
        'HEAD, GET, POST, PATCH, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response
