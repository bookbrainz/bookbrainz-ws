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


from bbschema import User
from flask.ext.restful import abort, marshal, reqparse, Resource
from sqlalchemy.orm.exc import NoResultFound

from . import db, structures


class UserResource(Resource):
    """ A Resource representing a User of the webservice. """
    def get(self, _id):
        try:
            user = db.session.query(User).filter_by(id=_id).one()
        except NoResultFound:
            abort(404)

        return marshal(user, structures.user)


class UserResourceList(Resource):
    """ A Resource representing a list of Users of the webservice. """

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        args = self.get_parser.parse_args()
        query = db.session.query(User).offset(args.offset).limit(args.limit)
        users = query.all()

        return marshal({
            'offset': args.offset,
            'count': len(users),
            'objects': users
        }, structures.user_list)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', type=unicode, required=True)
    post_parser.add_argument('email', type=unicode, required=True)
    post_parser.add_argument('user_type_id', type=unicode, required=True)

    def post(self):
        args = self.post_parser.parse_args()
        user = User(name=args.name, email=args.email,
                    user_type_id=args.user_type_id)
        db.session.add(user)
        db.session.commit()

        return marshal(user, structures.user)


def create_views(api):
    """ Create the views relating to Users, on the Restful API. """

    api.add_resource(UserResource, '/user/<int:_id>',
                     endpoint='user_get_single')
    api.add_resource(UserResourceList, '/user', endpoint='user_get_many')
