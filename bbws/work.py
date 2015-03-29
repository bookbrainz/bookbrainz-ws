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

from bbschema import Work, WorkData

from . import structures
from .entity import (EntityAliasResource, EntityAnnotationResource,
                     EntityDisambiguationResource, EntityResource,
                     EntityResourceList)


class WorkResource(EntityResource):
    entity_class = Work
    entity_fields = structures.work
    entity_data_fields = structures.work_data


class WorkResourceList(EntityResourceList):
    entity_class = Work
    entity_data_class = WorkData
    entity_data_fields = structures.work_data
    entity_stub_fields = structures.work_stub
    entity_list_fields = structures.work_list


def create_views(api):
    api.add_resource(WorkResource, '/work/<string:entity_gid>/',
                     endpoint='work_get_single')

    api.add_resource(
        EntityAliasResource, '/work/<string:entity_gid>/aliases',
        endpoint='work_get_aliases'
    )

    api.add_resource(
        EntityDisambiguationResource,
        '/work/<string:entity_gid>/disambiguation',
        endpoint='work_get_disambiguation'
    )

    api.add_resource(
        EntityAnnotationResource, '/work/<string:entity_gid>/annotation',
        endpoint='work_get_annotation'
    )

    api.add_resource(WorkResourceList, '/work/')
