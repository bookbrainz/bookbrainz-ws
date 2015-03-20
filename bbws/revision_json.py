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

from bbschema import (Relationship, RelationshipEntity, RelationshipText,
                      RelationshipTree)
from sqlalchemy.orm.exc import NoResultFound

from . import db


class JSONParseError(Exception):
    pass


def create_relationship(revision_json):
    relationship = Relationship()

    tree = RelationshipTree()
    tree.relationship_type_id = revision_json['relationship_type_id']

    for entity in revision_json.get('entities', []):
        rel_entity = RelationshipEntity(entity_gid=entity['gid'],
                                        position=entity['position'])
        tree.entities.append(rel_entity)

    for text in revision_json.get('text', []):
        rel_text = RelationshipText(text=text['text'],
                                    position=text['position'])
        tree.text.append(rel_text)

    return (relationship, tree)


def format_changes(base_revision_id, new_revision_id):
    """This analyzes the changes from one revision to another, and formats
    them into a single JSON structure for serving through the webservice.
    """

    # This may throw a "NoResultsFound" exception.
    new_revision = \
        db.session.query(EntityRevision).\
        filter_by(revision_id=new_revision_id).one()

    new_data = new_revision.entity_data
    new_annotation = (new_data.annotation.content
                      if new_data.annotation is not None else None)
    new_disambiguation = (new_data.disambiguation.comment
                          if new_data.disambiguation is not None else None)
    new_aliases = new_data.aliases

    if base_revision_id is None:
        base_data = None
        base_annotation = None
        base_disambiguation = None
        base_aliases = None
    else:
        base_revision = db.session.query(EntityRevision).filter_by(
            revision_id=base_revision_id
        ).one()
        base_data = base_revision.entity_data

        base_annotation = (base_data.annotation.content
                           if base_data.annotation is not None else None)
        base_disambiguation = (
            base_data.disambiguation.comment
            if base_data.disambiguation is not None else None
        )
        base_aliases = base_data.aliases

    return {
        'data': [base_data, new_data],
        'annotation': [base_annotation, new_annotation],
        'disambiguation': [base_disambiguation, new_disambiguation],
        'aliases': [base_aliases, new_aliases]
    }
