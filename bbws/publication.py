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

from bbschema import Publication

from . import structures
from .entity import (EntityResource, EntityAliasResource,
                     EntityDisambiguationResource, EntityAnnotationResource,
                     EntityResourceList)

class PublicationResource(EntityResource):
    entity_class = Publication
    entity_fields = structures.publication
    entity_data_fields = structures.publication_data


class PublicationResourceList(EntityResourceList):
    entity_class = Publication
    entity_list_fields = structures.publication_list


def create_views(api):
    api.add_resource(PublicationResource, '/publication/<string:entity_gid>/',
                     endpoint='publication_get_single')

    api.add_resource(
        EntityAliasResource, '/publication/<string:entity_gid>/aliases',
        endpoint='publication_get_aliases'
    )

    api.add_resource(
        EntityDisambiguationResource,
        '/publication/<string:entity_gid>/disambiguation',
        endpoint='publication_get_disambiguation'
    )

    api.add_resource(
        EntityAnnotationResource, '/publication/<string:entity_gid>/annotation',
        endpoint='publication_get_annotation'
    )

    api.add_resource(PublicationResourceList, '/publication/')
