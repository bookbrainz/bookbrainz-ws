# -*- coding: utf8 -*-

# Copyright (C) 2015 Sean Burke

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


""" This module contains the definitions for generic entity and entity-related
resources.
"""

from bbschema import Publisher, PublisherData

from . import structures
from .entity import (EntityAliasResource, EntityAnnotationResource,
                     EntityDisambiguationResource, EntityResource,
                     EntityResourceList)


class PublisherResource(EntityResource):
    entity_class = Publisher
    entity_fields = structures.publisher
    entity_data_fields = structures.publisher_data


class PublisherResourceList(EntityResourceList):
    entity_class = Publisher
    entity_data_class = PublisherData
    entity_data_fields = structures.publisher_data
    entity_stub_fields = structures.publisher_stub
    entity_list_fields = structures.publisher_list


def create_views(api):
    api.add_resource(PublisherResource, '/publisher/<string:entity_gid>/',
                     endpoint='publisher_get_single')

    api.add_resource(
        EntityAliasResource, '/publisher/<string:entity_gid>/aliases',
        endpoint='publisher_get_aliases'
    )

    api.add_resource(
        EntityDisambiguationResource,
        '/publisher/<string:entity_gid>/disambiguation',
        endpoint='publisher_get_disambiguation'
    )

    api.add_resource(
        EntityAnnotationResource, '/publisher/<string:entity_gid>/annotation',
        endpoint='publisher_get_annotation'
    )

    api.add_resource(PublisherResourceList, '/publisher/')
