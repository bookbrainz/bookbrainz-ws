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


from bbschema import Creator, Edition, Publication, Publisher, Work
from flask_restful import fields


TYPE_MAP = {
    Creator: 'creator_get_single',
    Publication: 'publication_get_single',
    Edition: 'edition_get_single',
    Publisher: 'publisher_get_single',
    Work: 'work_get_single'
}


class EntityUrl(fields.Url):
    def __init__(self, absolute=False, scheme=None):
        super(EntityUrl, self).__init__(None, absolute, scheme)

    def output(self, key, obj):
        if hasattr(obj, 'entity'):
            entity = obj.entity
        else:
            entity = obj

        # This will raise an exception if the entity type is invalid
        self.endpoint = TYPE_MAP[type(entity)]
        return super(EntityUrl, self).output(key, obj)


class CreatorUrl(fields.Url):
    def __init__(self, absolute=False, scheme=None):
        super(CreatorUrl, self).__init__('creator_get_single',
                                         absolute, scheme)

    def output(self, key, obj):
        obj.entity_gid = obj.creator_gid
        return super(CreatorUrl, self).output(key, obj)


class PublicationUrl(fields.Url):
    def __init__(self, absolute=False, scheme=None):
        super(PublicationUrl, self).__init__('publication_get_single',
                                             absolute, scheme)

    def output(self, key, obj):
        if obj.publication_gid is None:
            return None

        obj.entity_gid = obj.publication_gid
        return super(PublicationUrl, self).output(key, obj)


class PublisherUrl(fields.Url):
    def __init__(self, absolute=False, scheme=None):
        super(PublisherUrl, self).__init__('publisher_get_single',
                                           absolute, scheme)

    def output(self, key, obj):
        if obj.publisher_gid is None:
            return None

        obj.entity_gid = obj.publisher_gid
        return super(PublisherUrl, self).output(key, obj)

LANGUAGE_STUB = {
    'language_id': fields.Integer(attribute='id'),
    'name': fields.String
}

LANGUAGE = LANGUAGE_STUB.copy()
LANGUAGE.update({
    'iso_code_2t': fields.String,
    'iso_code_2b': fields.String,
    'iso_code_1': fields.String,
    'iso_code_3': fields.String,
    'frequency': fields.Integer
})

LANGUAGE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(LANGUAGE)),
}

ENTITY_ALIAS = {
    'alias_id': fields.Integer,
    'name': fields.String,
    'sort_name': fields.String,
    'language': fields.Nested(LANGUAGE_STUB, allow_null=True),
    'primary': fields.Boolean
}

DISPLAY_ALIAS = {
    'alias_id': fields.Integer,
    'name': fields.String,
    'sort_name': fields.String,
    'language': fields.Nested(LANGUAGE_STUB, allow_null=True),
    'primary': fields.Boolean
}

REVISION_STUB = {
    'revision_id': fields.Integer,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'note': fields.String,
    'user': fields.Nested({
        'user_id': fields.Integer,
    }),
    'parent_id': fields.Integer(default=None),
    'uri': fields.Url('revision_get_single', True)
}

ENTITY_REVISION = REVISION_STUB.copy()
ENTITY_REVISION.update({
    'entity_data_id': fields.Integer(default=None),
    'entity_uri': EntityUrl(True)
})

RELATIONSHIP_REVISION = REVISION_STUB.copy()
RELATIONSHIP_REVISION.update({
    'relationship_data_id': fields.Integer(default=None),
    'relationship_uri': fields.Url('relationship_get_single', True)
})


REVISION_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(REVISION_STUB))
}

ENTITY_REVISION_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(ENTITY_REVISION))
}


IDENTIFIER_TYPE_STUB = {
    'identifier_type_id': fields.Integer,
    'label': fields.String
}

IDENTIFIER_TYPE = IDENTIFIER_TYPE_STUB.copy()
IDENTIFIER_TYPE.update({
    'parent': fields.Nested(IDENTIFIER_TYPE_STUB, allow_null=True),
    'child_order': fields.Integer,
    'detection_regex': fields.String,
    'validation_regex': fields.String,
    'description': fields.String,
    'entity_type': fields.String
})


IDENTIFIER_TYPE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(IDENTIFIER_TYPE))
}


IDENTIFIER = {
    'identifier_id': fields.Integer,
    'identifier_type': fields.Nested(IDENTIFIER_TYPE_STUB),
    'value': fields.String
}


IDENTIFIER_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(IDENTIFIER))
}


ENTITY_STUB = {
    'entity_gid': fields.String,
    'uri': EntityUrl(True),
    '_type': fields.String
}

ENTITY = ENTITY_STUB.copy()
ENTITY.update({
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'aliases_uri': fields.Url('entity_get_aliases', True),
    'disambiguation_uri': fields.Url('entity_get_disambiguation', True),
    'annotation_uri': fields.Url('entity_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True),
    'revision': fields.Nested(ENTITY_REVISION)
})

ENTITY_DATA = {
    'default_alias': fields.Nested(ENTITY_ALIAS, allow_null=True)
}

ENTITY_ALIAS_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(ENTITY_ALIAS))
}


ENTITY_DISAMBIGUATION = {
    'disambiguation_id': fields.Integer(),
    'comment': fields.String()
}


ENTITY_ANNOTATION = {
    'annotation_id': fields.Integer(),
    'created_at': fields.DateTime(dt_format='iso8601'),
    'content': fields.String()
}


ENTITY_EXPANDED = ENTITY_STUB.copy()
ENTITY_EXPANDED.update({
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'disambiguation': fields.Nested(ENTITY_DISAMBIGUATION, allow_null=True),
    'annotation': fields.Nested(ENTITY_ANNOTATION, allow_null=True)
})

ENTITY_DIFF = {
    'annotation': fields.List(
        fields.Nested(ENTITY_ANNOTATION, allow_null=True)
    ),
    'disambiguation': fields.List(
        fields.Nested(ENTITY_DISAMBIGUATION, allow_null=True)
    ),
    'default_alias': fields.List(fields.Nested(ENTITY_ALIAS, allow_null=True)),
    'aliases': fields.List(fields.List(fields.Nested(ENTITY_ALIAS))),
    'identifiers': fields.List(fields.List(fields.Nested(IDENTIFIER)))
}


ENTITY_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(ENTITY_STUB))
}


RELATIONSHIP_STUB = {
    'relationship_id': fields.Integer,
    'uri': fields.Url('relationship_get_single', True)
}

RELATIONSHIP_TYPE_STUB = {
    'relationship_type_id': fields.Integer,
    'label': fields.String,
}

RELATIONSHIP_TYPE = RELATIONSHIP_TYPE_STUB.copy()
RELATIONSHIP_TYPE.update({
    'parent': fields.Nested(RELATIONSHIP_TYPE_STUB, allow_null=True),
    'child_order': fields.Integer,
    'description': fields.String,
    'template': fields.String,
    'deprecated': fields.Boolean,
})


RELATIONSHIP_TYPE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(RELATIONSHIP_TYPE))
}

RELATIONSHIP = RELATIONSHIP_STUB.copy()
RELATIONSHIP.update({
    'master_revision_id': fields.Integer,
    'last_updated': fields.DateTime(dt_format='iso8601'),
    'relationship_type': fields.Nested(
        RELATIONSHIP_TYPE,
        attribute='master_revision.relationship_data.relationship_type',
    ),
    'entities': fields.List(fields.Nested({
        'entity': fields.Nested(ENTITY_STUB),
        'position': fields.Integer
    }), attribute='master_revision.relationship_data.entities'),
    'texts': fields.List(fields.Nested({
        'text': fields.String,
        'position': fields.Integer
    }), attribute='master_revision.relationship_data.texts')
})

RELATIONSHIP_DIFF = {
    'relationship_type':
        fields.List(fields.Nested(RELATIONSHIP_TYPE, allow_null=True)),
    'entities': fields.List(fields.Nested({
        'entity': fields.Nested(ENTITY_STUB),
        'position': fields.Integer
    })),
    'texts': fields.List(fields.Nested({
        'text': fields.String,
        'position': fields.Integer
    }))
}


RELATIONSHIP_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(RELATIONSHIP))
}

USER_TYPE = {
    'user_type_id': fields.Integer,
    'label': fields.String
}

USER_TYPE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.Nested(USER_TYPE)
}

USER_STUB = {
    'user_id': fields.Integer,
    'name': fields.String
}

USER = USER_STUB.copy()
USER.update({
    'reputation': fields.Integer,
    'bio': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'active_at': fields.DateTime(dt_format='iso8601'),
    'user_type': fields.Nested(USER_TYPE),
    'total_revisions': fields.Integer,
    'revisions_applied': fields.Integer,
    'revisions_reverted': fields.Integer,
})

ACCOUNT = USER.copy()
ACCOUNT.update({
    'email': fields.String,
    'birth_date': fields.DateTime(dt_format='iso8601'),
    'gender': fields.Nested({
        'gender_id': fields.Integer(attribute='id'),
        'name': fields.String
    }, allow_null=True),
})

USER_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(USER))
}


# These fields definitions are specific to BookBrainz
CREATOR_STUB = ENTITY_STUB.copy()
CREATOR_STUB.update({
    'uri': fields.Url('creator_get_single', True)
})


CREATOR = ENTITY.copy()
CREATOR.update(CREATOR_STUB)
CREATOR.update({
    'aliases_uri': fields.Url('creator_get_aliases', True),
    'identifiers_uri': fields.Url('creator_get_identifiers', True),
    'disambiguation_uri': fields.Url('creator_get_disambiguation', True),
    'annotation_uri': fields.Url('creator_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


CREATOR_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(CREATOR_STUB))
}


CREATOR_DATA = ENTITY_DATA.copy()
CREATOR_DATA.update({
    'begin_date': fields.String(attribute='begin'),
    'begin_date_precision': fields.String,
    'end_date': fields.String(attribute='end'),
    'end_date_precision': fields.String,
    'ended': fields.Boolean,
    'creator_type': fields.Nested({
        'creator_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True),
    'gender': fields.Nested({
        'gender_id': fields.Integer(attribute='id'),
        'name': fields.String
    }, allow_null=True),
})

CREATOR_DIFF = ENTITY_DIFF.copy()
CREATOR_DIFF.update({
    'begin_date': fields.List(fields.String),
    'end_date': fields.List(fields.String),
    'ended': fields.List(fields.Boolean),
    'creator_type': fields.List(fields.Nested({
        'creator_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)),
    'gender': fields.List(fields.Nested({
        'gender_id': fields.Integer(attribute='id'),
        'name': fields.String
    }, allow_null=True))
})

PUBLICATION_STUB = ENTITY_STUB.copy()
PUBLICATION_STUB.update({
    'uri': fields.Url('publication_get_single', True)
})


PUBLICATION = ENTITY.copy()
PUBLICATION.update(PUBLICATION_STUB)
PUBLICATION.update({
    'aliases_uri': fields.Url('publication_get_aliases', True),
    'identifiers_uri': fields.Url('publication_get_identifiers', True),
    'disambiguation_uri': fields.Url('publication_get_disambiguation', True),
    'annotation_uri': fields.Url('publication_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True),
    'editions_uri': fields.Url('publication_get_editions', True)
})


PUBLICATION_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(PUBLICATION_STUB))
}


PUBLICATION_DATA = ENTITY_DATA.copy()
PUBLICATION_DATA.update({
    'publication_type': fields.Nested({
        'publication_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})

PUBLICATION_DIFF = ENTITY_DIFF.copy()
PUBLICATION_DIFF.update({
    'publication_type': fields.List(fields.Nested({
        'publication_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True))
})

PUBLISHER_STUB = ENTITY_STUB.copy()
PUBLISHER_STUB.update({
    'uri': fields.Url('publisher_get_single', True)
})


PUBLISHER = ENTITY.copy()
PUBLISHER.update(PUBLISHER_STUB)
PUBLISHER.update({
    'aliases_uri': fields.Url('publisher_get_aliases', True),
    'identifiers_uri': fields.Url('publisher_get_identifiers', True),
    'disambiguation_uri': fields.Url('publisher_get_disambiguation', True),
    'annotation_uri': fields.Url('publisher_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True),
    'editions_uri': fields.Url('publisher_get_editions', True)
})


PUBLISHER_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(PUBLISHER_STUB))
}


PUBLISHER_DATA = ENTITY_DATA.copy()
PUBLISHER_DATA.update({
    'begin_date': fields.String(attribute='begin'),
    'begin_date_precision': fields.String,
    'end_date': fields.String(attribute='end'),
    'end_date_precision': fields.String,
    'ended': fields.Boolean,
    'publisher_type': fields.Nested({
        'publisher_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})

PUBLISHER_DIFF = ENTITY_DIFF.copy()
PUBLISHER_DIFF.update({
    'begin_date': fields.List(fields.String),
    'end_date': fields.List(fields.String),
    'ended': fields.List(fields.Boolean),
    'publisher_type': fields.List(fields.Nested({
        'publisher_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True))
})


EDITION_STUB = ENTITY_STUB.copy()
EDITION_STUB.update({
    'uri': fields.Url('edition_get_single', True)
})


EDITION = ENTITY.copy()
EDITION.update(EDITION_STUB)
EDITION.update({
    'aliases_uri': fields.Url('edition_get_aliases', True),
    'identifiers_uri': fields.Url('edition_get_identifiers', True),
    'disambiguation_uri': fields.Url('edition_get_disambiguation', True),
    'annotation_uri': fields.Url('edition_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


EDITION_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(EDITION_STUB))
}


CREATOR_CREDIT_NAME = {
    'position': fields.Integer,
    'name': fields.String,
    'creator_uri': CreatorUrl(True),
    'join_phrase': fields.String
}


CREATOR_CREDIT = {
    'creator_credit_id': fields.Integer,
    'begin_phrase': fields.String,
    'names': fields.List(fields.Nested(CREATOR_CREDIT_NAME))
}


EDITION_DATA = ENTITY_DATA.copy()
EDITION_DATA.update({
    'publication_uri': PublicationUrl(True),
    'publisher_uri': PublisherUrl(True),
    'creator_credit': fields.Nested(CREATOR_CREDIT),
    'release_date': fields.String(attribute='release'),
    'release_date_precision': fields.String,
    'pages': fields.Integer(default=None),
    'height': fields.Integer(default=None),
    'width': fields.Integer(default=None),
    'depth': fields.Integer(default=None),
    'weight': fields.Integer(default=None),
    'language': fields.Nested({
        'language_id': fields.Integer(attribute='id'),
        'name': fields.String,
    }, allow_null=True),
    'edition_format': fields.Nested({
        'edition_format_id': fields.Integer,
        'label': fields.String
    }, allow_null=True),
    'edition_status': fields.Nested({
        'edition_status_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})

EDITION_DIFF = ENTITY_DIFF.copy()
EDITION_DIFF.update({
    'publication_uri': fields.List(PublicationUrl(True)),
    'publisher_uri': fields.List(PublisherUrl(True)),
    'release_date': fields.List(fields.String),
    'pages': fields.List(fields.Integer(default=None)),
    'height': fields.List(fields.Integer(default=None)),
    'width': fields.List(fields.Integer(default=None)),
    'depth': fields.List(fields.Integer(default=None)),
    'weight': fields.List(fields.Integer(default=None)),
    'language': fields.List(fields.Nested({
        'language_id': fields.Integer(attribute='id'),
        'name': fields.String,
    }, allow_null=True)),
    'edition_format': fields.List(fields.Nested({
        'edition_format_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)),
    'edition_status': fields.List(fields.Nested({
        'edition_status_id': fields.Integer,
        'label': fields.String
    }, allow_null=True))
})

WORK_STUB = ENTITY_STUB.copy()
WORK_STUB.update({
    'uri': fields.Url('work_get_single', True)
})


WORK = ENTITY.copy()
WORK.update(WORK_STUB)
WORK.update({
    'aliases_uri': fields.Url('work_get_aliases', True),
    'identifiers_uri': fields.Url('work_get_identifiers', True),
    'disambiguation_uri': fields.Url('work_get_disambiguation', True),
    'annotation_uri': fields.Url('work_get_annotation', True),
    'relationships_uri': fields.Url('relationship_get_many', True)
})


WORK_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(WORK_STUB))
}


WORK_DATA = ENTITY_DATA.copy()
WORK_DATA.update({
    'languages': fields.List(fields.Nested({
        'language_id': fields.Integer(attribute='id'),
        'name': fields.String,
    })),
    'work_type': fields.Nested({
        'work_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True)
})

WORK_DIFF = ENTITY_DIFF.copy()
WORK_DIFF.update({
    'languages': fields.List(fields.List(fields.Nested({
        'language_id': fields.Integer(attribute='id'),
        'name': fields.String,
    }))),
    'work_type': fields.List(fields.Nested({
        'work_type_id': fields.Integer,
        'label': fields.String
    }, allow_null=True))
})

PUBLICATION_TYPE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'publication_type_id': fields.Integer,
        'label': fields.String
    }))
}

CREATOR_TYPE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'creator_type_id': fields.Integer,
        'label': fields.String
    }))
}

PUBLISHER_TYPE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'publisher_type_id': fields.Integer,
        'label': fields.String
    }))
}

EDITION_FORMAT_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'edition_format_id': fields.Integer,
        'label': fields.String
    }))
}

EDITION_STATUS_ID = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'edition_status_id': fields.Integer,
        'label': fields.String
    }))
}

WORK_TYPE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'work_type_id': fields.Integer,
        'label': fields.String
    }))
}

GENDER_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested({
        'gender_id': fields.Integer(attribute='id'),
        'name': fields.String,
    }))
}

MESSAGE_RECEIPT = {
    'message_id': fields.Integer,
    'recipient': fields.Nested(USER_STUB),
    'archived': fields.Boolean,
}

MESSAGE_STUB = {
    'message_id': fields.Integer,
    'sender': fields.Nested(USER_STUB),
    'subject': fields.String,
}

MESSAGE = MESSAGE_STUB.copy()
MESSAGE.update({
    'message_id': fields.Integer,
    'sender': fields.Nested(USER_STUB),
    'subject': fields.String,
    'content': fields.String,
    'receipt': fields.Nested(MESSAGE_RECEIPT, allow_null=True)
})

MESSAGE_LIST = {
    'offset': fields.Integer,
    'count': fields.Integer,
    'objects': fields.List(fields.Nested(MESSAGE_STUB))
}
