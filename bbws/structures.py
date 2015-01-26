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


""" This module contains the field structure definitions for all of the
responses the webservice can provide. Fields can reference each other, but must
be declared in the correct order.
"""


from flask.ext.restful import fields

edit = {
    'id': fields.Integer,
    'status': fields.Integer,
    'uri': fields.Url('edit_get_single', True),
    'user': fields.Nested({
        'id': fields.Integer,
    }),
    'revisions_uri': fields.Url('revision_get_many', True)
}

edit_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(edit))
}

entity_stub = {
    'gid': fields.String,
    'uri': fields.Url('entity_get_single', True)
}


entity = entity_stub.copy()
entity.update({
    'master_revision_id': fields.Integer,
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'aliases_uri': fields.Url('entity_get_aliases', True),
    'disambiguation_uri': fields.Url('entity_get_disambiguation', True),
    'annotation_uri': fields.Url('entity_get_annotation', True),
    'data_uri': fields.Url('entity_get_data', True)
})


entity_alias = {
    'entity': fields.Nested(entity_stub),
    'aliases': fields.List(fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
        'sort_name': fields.String
    }))
}


entity_disambiguation = {
    'entity': fields.Nested(entity_stub),
    'disambiguation': fields.Nested({
        'id': fields.Integer(),
        'comment': fields.String()
    }, allow_null=True)
}


entity_annotation = {
    'entity': fields.Nested(entity_stub),
    'annotation': fields.Nested({
        'id': fields.Integer(),
        'created_at': fields.DateTime(dt_format='iso8601'),
        'content': fields.String()
    }, allow_null=True)
}


entity_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(entity))
}


relationship_stub = {
    'id': fields.Integer,
    'uri': fields.Url('relationship_get_single', True)
}

relationship = relationship_stub.copy()
relationship.update({
    'master_revision_id': fields.Integer,
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'relationship_type': fields.Integer(attribute='master_revision.relationship_tree.id'),
    'entities': fields.List(fields.Nested({
        'entity': fields.Nested(entity_stub),
        'position': fields.Integer
    }), attribute='master_revision.relationship_tree.entities'),
    'texts': fields.List(fields.Nested({
        'text': fields.String,
        'position': fields.Integer
    }), attribute='master_revision.relationship_tree.texts')
})


relationship_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(relationship_stub))
}

revision_stub = {
    'id': fields.Integer,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'user': fields.Nested({
        'id': fields.Integer,
    }),
    'uri': fields.Url('revision_get_single', True),
}

entity_revision = revision_stub.copy()
entity_revision.update({
    'entity': fields.Nested(entity_stub),
})

relationship_revision = revision_stub.copy()
relationship_revision.update({
    'relationship': fields.Nested(relationship_stub),
})


revision_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(revision_stub))
}

user_type = {
    'id': fields.Integer,
    'label': fields.String
}

user_type_list = {
    'objects': fields.Nested(user_type)
}

user_stub = {
    'id': fields.Integer,
    'name': fields.String
}

user = user_stub.copy()
user.update({
    'reputation': fields.Integer,
    'bio': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'active_at': fields.DateTime(dt_format='iso8601'),
    'stats_uri': fields.Url('editor_stats', True),
    'user_type': fields.Nested(user_type)
})

editor_stats = {
    'user': fields.Nested(user_stub),
    'total_edits': fields.Integer,
    'total_revisions': fields.Integer,
    'edits_accepted': fields.Integer,
    'edits_rejected': fields.Integer,
    'edits_failed': fields.Integer,
}


user_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(user))
}


# These fields definitions are specific to BookBrainz


creator_data = {
    'id': fields.Integer,
    'begin_date': fields.DateTime(dt_format='iso8601'),
    'begin_date_precision': fields.String,
    'end_date': fields.DateTime(dt_format='iso8601'),
    'end_date_precision': fields.String,
    'ended': fields.Boolean,
    'creator_type': fields.Nested({
        'id': fields.Integer,
        'label': fields.String
    })
}


publication_data = {
    'id': fields.Integer,
    'publication_type': fields.Nested({
        'id': fields.Integer,
        'label': fields.String
    })
}

publication_type_list = {
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'id': fields.Integer,
        'label': fields.String
    }))
}
