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

language_stub = {
    'language_id': fields.Integer,
    'name': fields.String
}

language = language_stub.copy()
language.update(
    'iso_code_2t': fields.String,
    'iso_code_2b': fields.String,
    'iso_code_1': fields.String,
    'iso_code_3': fields.String,
)

language_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(language)),
}

edit = {
    'edit_id': fields.Integer,
    'status': fields.Integer,
    'uri': fields.Url('edit_get_single', True),
    'user': fields.Nested({
        'user_id': fields.Integer,
    }),
    'revisions_uri': fields.Url('revision_get_many', True)
}

edit_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(edit))
}

entity_alias = {
    'alias_id': fields.Integer,
    'name': fields.String,
    'sort_name': fields.String,
    'language': fields.Nested(language_stub, allow_null=True),
    'primary': fields.Boolean
}

revision_stub = {
    'revision_id': fields.Integer,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'note': fields.String,
    'user': fields.Nested({
        'user_id': fields.Integer,
    }),
    'uri': fields.Url('revision_get_single', True),
}

entity_stub = {
    'entity_gid': fields.String,
    'uri': fields.Url('entity_get_single', True)
}


entity = entity_stub.copy()
entity.update({
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'aliases_uri': fields.Url('entity_get_aliases', True),
    'disambiguation_uri': fields.Url('entity_get_disambiguation', True),
    'annotation_uri': fields.Url('entity_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True),
    'revision': fields.Nested(revision_stub)
})

entity_data = {
    'default_alias': fields.Nested(entity_alias, allow_null=True)
}

entity_alias_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(entity_alias))
}


entity_disambiguation = {
    'disambiguation_id': fields.Integer(),
    'comment': fields.String()
}


entity_annotation = {
    'annotation_id': fields.Integer(),
    'created_at': fields.DateTime(dt_format='iso8601'),
    'content': fields.String()
}


entity_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(entity_stub))
}


relationship_stub = {
    'relationship_id': fields.Integer,
    'uri': fields.Url('relationship_get_single', True)
}

relationship_type_stub = {
    'relationship_type_id': fields.Integer,
    'label': fields.String,
}

relationship_type = relationship_type_stub.copy()
relationship_type.update({
    'parent': fields.Nested(relationship_type_stub, allow_null=True),
    'child_order': fields.Integer,
    'description': fields.String,
    'template': fields.String,
    'deprecated': fields.Boolean,
})


relationship_type_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(relationship_type))
}

relationship = relationship_stub.copy()
relationship.update({
    'master_revision_id': fields.Integer,
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'relationship_type': fields.Nested(
        relationship_type,
        attribute='master_revision.relationship_tree.relationship_type',
    ),
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
    'objects': fields.List(fields.Nested(relationship))
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
    'user_type_id': fields.Integer,
    'label': fields.String
}

user_type_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.Nested(user_type)
}

user_stub = {
    'user_id': fields.Integer,
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

account = user.copy()
account.update({
    'email': fields.String,
    'birth_date': fields.DateTime(dt_format='iso8601'),
    'gender_id': fields.Integer
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
creator_stub = entity_stub.copy()
creator_stub.update({
    'uri': fields.Url('creator_get_single', True)
})


creator = entity.copy()
creator.update(creator_stub)
creator.update({
    'aliases_uri': fields.Url('creator_get_aliases', True),
    'disambiguation_uri': fields.Url('creator_get_disambiguation', True),
    'annotation_uri': fields.Url('creator_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


creator_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(creator_stub))
}


creator_data = entity_data.copy()
creator_data.update({
    'begin_date': fields.String,
    'begin_date_precision': fields.String,
    'end_date': fields.String,
    'end_date_precision': fields.String,
    'ended': fields.Boolean,
    'creator_type': fields.Nested({
        'creator_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True),
    'gender': fields.Nested({
        'gender_id': fields.Integer,
        'name': fields.String
    }, allow_null=True),
})


publication_stub = entity_stub.copy()
publication_stub.update({
    'uri': fields.Url('publication_get_single', True)
})


publication = entity.copy()
publication.update(publication_stub)
publication.update({
    'aliases_uri': fields.Url('publication_get_aliases', True),
    'disambiguation_uri': fields.Url('publication_get_disambiguation', True),
    'annotation_uri': fields.Url('publication_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


publication_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(publication_stub))
}


publication_data = entity_data.copy()
publication_data.update({
    'publication_type': fields.Nested({
        'publication_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})


publisher_stub = entity_stub.copy()
publisher_stub.update({
    'uri': fields.Url('publisher_get_single', True)
})


publisher = entity.copy()
publisher.update(publisher_stub)
publisher.update({
    'aliases_uri': fields.Url('publisher_get_aliases', True),
    'disambiguation_uri': fields.Url('publisher_get_disambiguation', True),
    'annotation_uri': fields.Url('publisher_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


publisher_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(publisher_stub))
}


publisher_data = entity_data.copy()
publisher_data.update({
    'begin_date': fields.String,
    'begin_date_precision': fields.String,
    'end_date': fields.String,
    'end_date_precision': fields.String,
    'ended': fields.Boolean,
    'publisher_type': fields.Nested({
        'publisher_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})


edition_stub = entity_stub.copy()
edition_stub.update({
    'uri': fields.Url('edition_get_single', True)
})


edition = entity.copy()
edition.update(edition_stub)
edition.update({
    'aliases_uri': fields.Url('edition_get_aliases', True),
    'disambiguation_uri': fields.Url('edition_get_disambiguation', True),
    'annotation_uri': fields.Url('edition_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


edition_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(edition_stub))
}


edition_data = entity_data.copy()
edition_data.update({
    'begin_date': fields.String,
    'begin_date_precision': fields.String,
    'end_date': fields.String,
    'end_date_precision': fields.String,
    'ended': fields.Boolean,
    'language': fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
    }, allow_null=True),
    'edition_status': fields.Nested({
        'edition_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})


work_stub = entity_stub.copy()
work_stub.update({
    'uri': fields.Url('work_get_single', True)
})


work = entity.copy()
work.update(work_stub)
work.update({
    'aliases_uri': fields.Url('work_get_aliases', True),
    'disambiguation_uri': fields.Url('work_get_disambiguation', True),
    'annotation_uri': fields.Url('work_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


work_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(work_stub))
}


work_data = entity_data.copy()
work_data.update({
    'languages': fields.List(fields.Nested({
        'id': fields.Integer,
        'name': fields.String,
    })),
    'work_type': fields.Nested({
        'work_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})


publication_type_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'publication_type_id': fields.Integer,
        'label': fields.String
    }))
}

creator_type_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'creator_type_id': fields.Integer,
        'label': fields.String
    }))
}

publisher_type_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'publisher_type_id': fields.Integer,
        'label': fields.String
    }))
}

edition_type_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'edition_type_id': fields.Integer,
        'label': fields.String
    }))
}

work_type_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'work_type_id': fields.Integer,
        'label': fields.String
    }))
}

gender_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'gender_id': fields.Integer,
        'name': fields.String,
    }))
}

message_receipt = {
    'message_id': fields.Integer,
    'recipient': fields.Nested(user_stub),
    'archived': fields.Boolean,
}

message_stub = {
    'message_id': fields.Integer,
    'sender': fields.Nested(user_stub),
    'subject': fields.String,
}

message = message_stub.copy()
message.update({
    'message_id': fields.Integer,
    'sender': fields.Nested(user_stub),
    'subject': fields.String,
    'content': fields.String,
    'receipt': fields.Nested(message_receipt, allow_null=True)
})

message_list = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(message_stub))
}
