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

from bbschema import (Edition, EditionData)

from . import structures
from .entity import (EntityResource, EntityAliasResource,
                     EntityDisambiguationResource, EntityAnnotationResource,
                     EntityResourceList)

class EditionResource(EntityResource):
    entity_class = Edition
    entity_fields = structures.edition
    entity_data_fields = structures.edition_data


class EditionResourceList(EntityResourceList):
    entity_class = Edition
    entity_data_class = EditionData
    entity_stub_fields = structures.edition_stub
    entity_list_fields = structures.edition_list


def create_views(api):
    api.add_resource(EditionResource, '/edition/<string:entity_gid>/',
                     endpoint='edition_get_single')

    api.add_resource(
        EntityAliasResource, '/edition/<string:entity_gid>/aliases',
        endpoint='edition_get_aliases'
    )

    api.add_resource(
        EntityDisambiguationResource,
        '/edition/<string:entity_gid>/disambiguation',
        endpoint='edition_get_disambiguation'
    )

    api.add_resource(
        EntityAnnotationResource, '/edition/<string:entity_gid>/annotation',
        endpoint='edition_get_annotation'
    )

    api.add_resource(EditionResourceList, '/edition/')
