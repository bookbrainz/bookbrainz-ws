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
    def get(self, user_id):
        """Get information about a single User of the webservice.

        :param int user_id: the ID of the user to get information about

        :>json int user_id: the ID of the resulting user
        :>json int reputation: the user's reputation
        :>json string bio: the user-written bio
        :>json datetime created_at: the date and time the user was created
        :>json datetime active_at: the date and time when the user was last active
        :>json user_type: the UserType for the user
        :>json int total_revisions: the total number of revision made by the user
        :>json int revisions_applied: the number of revisions by the user that have
            been applied
        :>json int revisions_reverted: the number of revisions by the user that
            have been reverted
        :status 404: when the requested user was not found in the database
        """

        try:
            user = db.session.query(User).filter_by(user_id=user_id).one()
        except NoResultFound:
            abort(404)

        return marshal(user, structures.USER)

    @oauth_provider.require_oauth()
    def put(self, user_id):
        """ Update information about a single User of the webservice. Currently
        only allows updating the user bio. Requires authentication. For response
        format, see :ref:`GET /user/(int: id)/ <user-get>`

        :param int user_id: the ID of the user to update information for

        :<json string bio: the updated bio for the specified user

        :>json int user_id: the ID of the resulting user
        :>json int eputation: the user's reputation
        :>json string bio: the user-written bio
        :>json datetime created_at: the date and time the user was created
        :>json datetime active_at: the date and time when the user was last active
        :>json user_type: the UserType for the user
        :>json int total_revisions: the total number of revision made by the user
        :>json int revisions_applied: the number of revisions by the user that have
            been applied
        :>json int revisions_reverted: the number of revisions by the user that
            have been reverted
        :status 404: when the requested user was not found in the database
        """

        if user_id != request.oauth.user.user_id:
            abort(401)

        try:
            user = db.session.query(User).filter_by(user_id=user_id).one()
        except NoResultFound:
            abort(404)

        json = request.get_json()

        user.bio = json['bio']

        db.session.commit()

        return marshal(user, structures.USER)


class AccountResource(Resource):
    @oauth_provider.require_oauth()
    def get(self):
        """Get private information about the currently authenticated User.

        :<header Authorization: the access token to use for the request

        :>json int user_id: the ID of the resulting user
        :>json int reputation: the user's reputation
        :>json string bio: the user-written bio
        :>json datetime created_at: the date and time the user was created
        :>json datetime active_at: the date and time when the user was last active
        :>json user_type: the UserType for the user
        :>json int total_revisions: the total number of revision made by the user
        :>json int revisions_applied: the number of revisions by the user that have
            been applied
        :>json int revisions_reverted: the number of revisions by the user that
            have been reverted
        :>json string email: the user's registered email address
        :>json date birth_date: the date of birth of the user
        :>json gender: the gender of the user
        :status 404: when the requested user was not found in the database
        """
        return marshal(request.oauth.user, structures.ACCOUNT)


class UserResourceList(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('limit', type=int, default=20)
    get_parser.add_argument('offset', type=int, default=0)

    def get(self):
        """Get a list of webservice users, with some information about each.

        :query int offset: the requested offset of the first result
        :query int limit: the maximum number of users to list

        :>json offset: the offset of the first result, as specified by the user
        :>json count: the number of results returned, less than or equal to the
            limit parameter
        :>json objects: an array of users
        """

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
        # noinspection PyPep8
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
        # noinspection PyPep8
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
                     endpoint='user_single')
    api.add_resource(UserTypeResourceList, '/userType/')
    api.add_resource(UserResourceList, '/user/', endpoint='user_many')

    api.add_resource(AccountResource, '/account/',
                     endpoint='account_current')

    api.add_resource(UserMessageResource, '/message/<int:message_id>')
    api.add_resource(UserMessageInboxResource, '/message/inbox/')
    api.add_resource(UserMessageArchiveResource, '/message/archive/')
    api.add_resource(UserMessageSentResource, '/message/sent/')
