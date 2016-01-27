# -*- coding: utf8 -*-

# Copyright (C) 2015, 2016 Stanisław Szcześniak

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

from bbschema import (Creator, CreatorData, CreatorType, EntityRevision,
                      Publication, PublicationData, PublicationType,
                      RelationshipRevision, RelationshipData, RelationshipType,
                      User, UserType, OAuthClient, EditionFormat, EditionStatus,
                      Language, Work, WorkData, WorkType, Gender, Edition,
                      EditionData, Publisher, PublisherData, PublisherType,
                      IdentifierType)

from args_generators import *
import sample_data_helper_functions


def load_data(db):
    """ Generates sample random data in the database

    All the instances except User instances are generated using
    add_entities function. It takes as an optional argument a
    function which should generate arguments for the given class
    initialization in the form of dictionary.

    Args generator example:
    def languages_args_generator():
        result = {}
        result['name'] = u'Esperanto'
        return result

    add_entities usage example:
        add_entities(database, Language, languages_args_generator, 3, 7)

    This example would add the random number (between 3 and 7)
    of Language instances, which are filled in with languages_args_generator.
    In this case, all the languages would have name = u'Esperanto', because
    this generator always returns the same arguments.

    :param db: database to add the data into
    :return: None
    """

    db.session.execute("TRUNCATE TABLE musicbrainz.language CASCADE")
    db.session.execute("TRUNCATE TABLE musicbrainz.gender CASCADE")
    db.session.commit()

    languages = add_entities(db, Language, get_languages_args_generator(),
                             LANGUAGES_COUNT, LANGUAGES_COUNT)
    random.choice(languages).name = u'English'
    sample_data_helper_functions.all_languages = languages

    genders = add_entities(db, Gender, get_genders_args_generator(),
                           GENDERS_COUNT, GENDERS_COUNT)
    sample_data_helper_functions.all_genders = genders

    db.session.commit()

    editor_type = UserType(label=u'Editor')
    db.session.add(editor_type)
    db.session.commit()

    editor = User(name=u'Bob',
                  password=u'$2b$12$AJTVpce37LM9Dk93qzRe.'
                           u'eMSw1ivsAmoa037.eS6VXoLAyK9cy0YG',
                  email=u'bob@bobville.org',
                  user_type_id=editor_type.user_type_id)
    sample_data_helper_functions.main_editor = editor
    db.session.add(editor)
    editor.languages = generate_user_languages(editor)

    db.session.commit()
    client = OAuthClient(client_id='9ab9da7e-a7a3-4f86-87c6-bf8b4b8213c7',
                         owner_id=editor.user_id)
    db.session.add(client)
    db.session.commit()

    edition_formats = \
        add_entities(
            db, EditionFormat, only_label_args_generator,
            EDITION_FORMATS, EDITION_FORMATS
        )

    edition_statuses = \
        add_entities(
            db, EditionStatus, only_label_args_generator,
            EDITION_STATUSES, EDITION_STATUSES
        )

    sample_data_helper_functions.all_edition_formats = edition_formats
    sample_data_helper_functions.all_edition_statuses = edition_statuses

    db.session.commit()

    """
        Adding EntityType objects
    """

    creator_types = \
        add_entities(db, CreatorType, only_label_args_generator)
    publication_types = \
        add_entities(db, PublicationType, only_label_args_generator)
    work_types = \
        add_entities(db, WorkType, only_label_args_generator)
    publisher_types = \
        add_entities(db, PublisherType, only_label_args_generator)
    relationship_types = \
        add_entities(db, RelationshipType, relationship_type_args_generator)
    identifier_types = \
        add_entities(db, IdentifierType, identifier_type_args_generator)

    db.session.commit()

    sample_data_helper_functions.all_creator_types = creator_types
    sample_data_helper_functions.all_publisher_types = publisher_types
    sample_data_helper_functions.all_publication_types = publication_types
    sample_data_helper_functions.all_work_types = work_types
    sample_data_helper_functions.all_relationship_types = relationship_types
    sample_data_helper_functions.all_identifier_types = identifier_types

    creator_entities = add_entities(db, Creator)
    publication_entities = add_entities(db, Publication)
    work_entities = add_entities(db, Work)
    edition_entities = add_entities(db, Edition)
    publisher_entities = add_entities(db, Publisher)
    relationship_entities = add_entities(db, Relationship)

    sample_data_helper_functions.all_publishers = publisher_entities
    sample_data_helper_functions.all_publications = publication_entities

    db.session.commit()

    """
        Adding EntityData objects
    """

    creator_data_entities = \
        add_entities(db, CreatorData,
                     get_creator_data_args_generator(creator_types),
                     len(creator_entities), len(creator_entities))
    publication_data_entities = \
        add_entities(db, PublicationData,
                     get_publication_data_args_generator(publication_types),
                     len(publication_entities), len(publication_entities))
    work_data_entities = \
        add_entities(db, WorkData,
                     get_work_data_args_generator(work_types, languages),
                     len(work_entities), len(work_entities))
    publisher_data_entities = \
        add_entities(db, PublisherData,
                     get_publisher_data_args_generator(publisher_types),
                     len(publisher_entities), len(publisher_entities))

    db.session.commit()

    edition_data_entities = \
        add_entities(db, EditionData,
                     get_edition_data_args_generator(
                         publisher_entities,
                         publication_entities,
                         languages,
                         edition_formats,
                         edition_statuses
                     ),
                     len(edition_entities), len(edition_entities))

    db.session.commit()

    """
        EntityRevisions adding

        All entities are copied to one list and so is their data.
        Then the revisions are created that contain consecutive pairs
        from this lists. The revisions list is reversed because
        get_entity_revision_args_generator is getting elements starting
        from the last ones.
    """

    all_entities = creator_entities + publication_entities + \
        work_entities + edition_entities + publisher_entities

    all_entities_data = creator_data_entities + publication_data_entities + \
        work_data_entities + edition_data_entities + \
        publisher_data_entities

    all_revisions = \
        add_entities(
            db, EntityRevision,
            get_entity_revision_args_generator(
                editor,
                all_entities,
                all_entities_data),
            len(all_entities), len(all_entities))
    all_revisions.reverse()

    for i in range(len(all_entities)):
        all_entities[i].master_revision = all_revisions[i]

    db.session.commit()

    """
        Adding relationships
        Relationship entities are randomly generated from already created
        entities of all types.
    """
    relationship_data_entities = \
        add_entities(db, RelationshipData,
                     get_relationship_data_args_generator(
                         relationship_types, all_entities),
                     len(relationship_entities), len(relationship_entities))

    db.session.commit()

    relationship_revisions = \
        add_entities(
            db, RelationshipRevision,
            get_entity_revision_args_generator(
                editor,
                relationship_entities,
                relationship_data_entities),
            len(relationship_entities), len(relationship_entities))
    relationship_revisions.reverse()

    for i in range(len(relationship_entities)):
        relationship_entities[i].master_revision = relationship_revisions[i]

    db.session.commit()
