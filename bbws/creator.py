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

from bbschema import Creator, CreatorData

from . import structures
from .entity import (EntityAliasResource, EntityAnnotationResource,
                     EntityDisambiguationResource, EntityResource,
                     EntityResourceList)


class CreatorResource(EntityResource):
    entity_class = Creator
    entity_fields = structures.creator
    entity_data_fields = structures.creator_data
    entity_stub_fields = structures.creator_stub


class CreatorResourceList(EntityResourceList):
    entity_class = Creator
    entity_data_class = CreatorData
    entity_data_fields = structures.creator_data
    entity_stub_fields = structures.creator_stub
    entity_list_fields = structures.creator_list


def create_views(api):
    api.add_resource(CreatorResource, '/creator/<string:entity_gid>/',
                     endpoint='creator_get_single')

    api.add_resource(
        EntityAliasResource, '/creator/<string:entity_gid>/aliases',
        endpoint='creator_get_aliases'
    )

    api.add_resource(
        EntityDisambiguationResource,
        '/creator/<string:entity_gid>/disambiguation',
        endpoint='creator_get_disambiguation'
    )

    api.add_resource(
        EntityAnnotationResource, '/creator/<string:entity_gid>/annotation',
        endpoint='creator_get_annotation'
    )

    api.add_resource(CreatorResourceList, '/creator/')
