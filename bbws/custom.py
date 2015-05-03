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

from elasticsearch import Elasticsearch
from flask import jsonify, request
from flask.ext.restful import abort, marshal
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from bbschema import (Alias, Creator, Edition, Entity, Publication, Publisher,
                      Work)

from . import cache, db, structures

es = Elasticsearch()

TYPE_MAP = {
    Creator: structures.creator_data,
    Publication: structures.publication_data,
    Edition: structures.edition_data,
    Publisher: structures.publisher_data,
    Work: structures.work_data
}


def index_entity(entity):
    es.index(
        index='bookbrainz',
        doc_type=entity['_type'].lower(),
        id=entity['entity_gid'],
        body=entity
    )


def init(app):
    # Book of the Week
    @app.route('/botw', methods=['GET'])
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

    @app.route('/search/', endpoint='search_query', methods=['GET'])
    def search():
        query = request.args.get('q', '')
        mode = request.args.get('mode', 'search')

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

        return jsonify(es.search(index='bookbrainz', body=query_obj))

    @app.route('/search/reindex', endpoint='search_reindex', methods=['GET'])
    def reindex_search():
        entities = db.session.query(Entity).options(
            joinedload('master_revision.entity_data')
        ).all()

        for entity in entities:
            entity_out = marshal(entity, structures.entity_expanded)
            data_out = marshal(entity.master_revision.entity_data,
                               TYPE_MAP[type(entity)])

            entity_out.update(data_out)
            index_entity(entity_out)

        return jsonify({'success': True})
