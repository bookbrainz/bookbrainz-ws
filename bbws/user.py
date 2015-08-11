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


import bcrypt
from bbschema import Message, MessageReceipt, User, UserType
from flask import request
from flask_restful import Resource, abort, marshal, reqparse
from sqlalchemy.orm.exc import NoResultFound

from . import structures
from .services import db, oauth_provider


class UserResource(Resource):
    """ A Resource representing a User of the webservice. """
    def get(self, user_id):
        try:
            user = db.session.query(User).filter_by(user_id=user_id).one()
        except NoResultFound:
            abort(404)

        return marshal(user, structures.USER)

    def put(self, user_id):
        try:
            user = db.session.query(User).filter_by(user_id=user_id).one()
        except NoResultFound:
            abort(404)

        json = request.get_json()

        user.bio = json['bio']

        db.session.commit()

        return marshal(user, structures.USER)


class AccountResource(Resource):
    """ Provides the user's own secrets for authenticated users. """

    @oauth_provider.require_oauth()
    def get(self):
        return marshal(request.oauth.user, structures.ACCOUNT)


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
        }, structures.USER_LIST)

    def post(self):
        json = request.get_json()

        try:
            # Use bcrypt to generate a salted password hash
            password = json['password'].encode('utf-8')
            password = bcrypt.hashpw(password, bcrypt.gensalt())

            user = User(name=json['name'], email=json['email'],
                        user_type_id=json['user_type']['user_type_id'],
                        password=password)
        except KeyError:
            abort(400)

        db.session.add(user)
        db.session.commit()

        return marshal(user, structures.USER)


class UserTypeResourceList(Resource):
    def get(self):
        types = db.session.query(UserType).all()
        return marshal({
            'offset': 0,
            'count': len(types),
            'objects': types
        }, structures.USER_TYPE_LIST)


class UserMessageResource(Resource):

    @oauth_provider.require_oauth()
    def get(self, message_id):
        try:
            message = db.session.query(Message).\
                filter_by(message_id=message_id).one()
        except NoResultFound:
            abort(404)

        # We have a message - check that the user should see it
        for receipt in message.receipts:
            if receipt.recipient_id == request.oauth.user.user_id:
                message.receipt = receipt
                data = marshal(message, structures.MESSAGE)
                # For now, archive the message once GET has run once
                message.receipt.archived = True
                db.session.commit()
                return data

        if message.sender_id == request.oauth.user.user_id:
            return marshal(message, structures.MESSAGE)

        abort(401)  # Unauthorized


class UserMessageInboxResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    @oauth_provider.require_oauth()
    def get(self):
        args = self.get_parser.parse_args()
        messages = db.session.query(Message).join(MessageReceipt).\
            filter(MessageReceipt.recipient_id == request.oauth.user.user_id).\
            filter(MessageReceipt.archived == False).\
            offset(args.offset).limit(args.limit).all()

        return marshal({
            'offset': args.offset,
            'count': len(messages),
            'objects': messages
        }, structures.MESSAGE_LIST)


class UserMessageArchiveResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    @oauth_provider.require_oauth()
    def get(self):
        args = self.get_parser.parse_args()
        messages = db.session.query(Message).join(MessageReceipt).\
            filter(MessageReceipt.recipient_id == request.oauth.user.user_id).\
            filter(MessageReceipt.archived == True).\
            offset(args.offset).limit(args.limit).all()

        return marshal({
            'offset': args.offset,
            'count': len(messages),
            'objects': messages
        }, structures.MESSAGE_LIST)


class UserMessageSentResource(Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    @oauth_provider.require_oauth()
    def get(self):
        args = self.get_parser.parse_args()
        messages = db.session.query(Message).\
            filter(Message.sender_id == request.oauth.user.user_id).\
            offset(args.offset).limit(args.limit).all()

        return marshal({
            'offset': args.offset,
            'count': len(messages),
            'objects': messages
        }, structures.MESSAGE_LIST)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('recipient_ids', type=int, action='append',
                             required=True)
    post_parser.add_argument('subject', type=unicode, required=True)
    post_parser.add_argument('content', type=unicode, required=True)

    @oauth_provider.require_oauth()
    def post(self):
        """ Add a new message to the sent messages list, to the recipients
        indicated in the POST body.
        """
        args = self.post_parser.parse_args()

        new_message = Message(sender_id=request.oauth.user.user_id,
                              subject=args.subject, content=args.content)

        recipients = []
        try:
            for recipient_id in args.recipient_ids:
                recipients.append(db.session.query(User).
                                  filter_by(user_id=recipient_id).one())
        except NoResultFound:
            abort(404)

        for recipient in recipients:
            receipt = MessageReceipt()
            receipt.recipient = recipient
            new_message.receipts.append(receipt)

        db.session.add(new_message)
        db.session.commit()

        return marshal(new_message, structures.MESSAGE)


def create_views(api):
    """ Create the views relating to Users, on the Restful API. """

    api.add_resource(UserResource, '/user/<int:user_id>/',
                     endpoint='user_get_single')
    api.add_resource(UserTypeResourceList, '/userType/')
    api.add_resource(UserResourceList, '/user/', endpoint='user_get_many')

    api.add_resource(AccountResource, '/account/',
                     endpoint='account_get_current')

    api.add_resource(UserMessageResource, '/message/<int:message_id>')
    api.add_resource(UserMessageInboxResource, '/message/inbox/')
    api.add_resource(UserMessageArchiveResource, '/message/archive/')
    api.add_resource(UserMessageSentResource, '/message/sent/')
