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


from bbschema import Creator, Edition, Entity, Publication, Publisher, Work
from elasticsearch import Elasticsearch
from flask import jsonify, request
from flask_restful import abort, marshal
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import structures
from .services import cache, db
from .util import index_entity, is_uuid


TYPE_MAP = {
    Creator: structures.CREATOR_DATA,
    Publication: structures.PUBLICATION_DATA,
    Edition: structures.EDITION_DATA,
    Publisher: structures.PUBLISHER_DATA,
    Work: structures.WORK_DATA
}


def init(app):
    # Book of the Week
    @app.route('/botw', methods=['GET'])
    def botw():
        # pylint: disable=unused-variable
        stored_gid = cache.get('botw')
        if stored_gid is None:
            abort(404)

        try:
            entity = db.session.query(Entity).\
                filter_by(entity_gid=stored_gid).one()
        except NoResultFound:
            abort(404)

        return jsonify(marshal(entity, structures.ENTITY))

    @app.route('/search/', endpoint='search_query', methods=['GET'])
    def search():
        # pylint: disable=unused-variable
        query = request.args.get('q', '')
        mode = request.args.get('mode', 'search')
        collection = request.args.get('collection')

        if collection not in ['creator',
                              'publication',
                              'edition',
                              'publisher',
                              'work']:
            collection = None

        if is_uuid(query):
            # Query by UUID, directly against stored IDs
            query_obj = {
                'query': {
                    'ids': {
                        "values": [query]
                    }
                }
            }
        else:
            search_field = 'default_alias.name'

            if mode == 'search':
                search_field += '.search'
            elif mode == 'auto':
                search_field += '.autocomplete'

            query_obj = {
                'query': {
                    'match': {
                        search_field: {
                            'query': query,
                            'minimum_should_match': '80%'
                        }
                    }
                }
            }

        es_conn = Elasticsearch()
        search = es_conn.search(
            index='bookbrainz',
            doc_type=collection,
            body=query_obj
        )

        return jsonify(search['hits'])

    @app.route('/search/reindex', endpoint='search_reindex', methods=['GET'])
    def reindex_search():
        # pylint: disable=unused-variable
        entities = db.session.query(Entity).options(
            joinedload('master_revision.entity_data')
        ).all()

        es_conn = Elasticsearch()
        for entity in entities:
            entity_out = marshal(entity, structures.ENTITY_EXPANDED)
            data_out = marshal(entity.master_revision.entity_data,
                               TYPE_MAP[type(entity)])

            entity_out.update(data_out)
            index_entity(es_conn, entity_out)

        return jsonify({'success': True})
