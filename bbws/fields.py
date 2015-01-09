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


""" This module contains the field definitions for all of the responses the
webservice can provide. Fields can reference each other, but must be declared
in the correct order.
"""


from flask.ext.restful import fields


user = {
    'name': fields.String,
    'reputation': fields.Integer,
    'bio': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'active_at': fields.DateTime(dt_format='iso8601'),
}


user_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(user))
}
