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

""" This module defines custom (non-resource) routes in the webservice. These
should be kept to a minimum.
"""

from flask import jsonify
from flask.ext.restful import abort, marshal

from bbschema import Entity
from sqlalchemy.orm.exc import NoResultFound

from . import cache, db, structures


def init(app):
    # Book of the Week
    @app.route('/ws/botw', methods=['GET'])
    def botw():
        stored_gid = cache.get('botw')
        if stored_gid is None:
            abort(404)

        try:
            entity = db.session.query(Entity).\
                filter_by(entity_gid=stored_gid).one()
        except NoResultFound:
            abort(404)

        return jsonify(marshal(entity, structures.entity))
