from flask.ext.testing import TestCase

from bbschema import (EntityRevision, EntityTree, PublicationData,
                      create_all)
from bbws import create_app, db, revision_json

from .fixture import load_data


class TestRevisionJSON(TestCase):
    def create_app(self):
        return create_app('../config/test.py')

    def setUp(self):
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")
        db.engine.execute("CREATE SCHEMA bookbrainz")
        create_all(db.engine)
        load_data(db)

    def tearDown(self):
        db.session.remove()
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")

    def test_create_entity(self):
        entity_tree = revision_json.parse_changes({
            'entity_gid': None,
            'publication_data': {
                'publication_type_id': 1
            },
            'annotation': "Testing this entity, so don't actually use this.",
            'disambiguation': "A disambiguation.",
            'aliases': [
                {
                    'name': 'ABC',
                    'sort_name': 'CBA',
                    'language_id': 1,
                    'default': False,
                    'primary': True
                }
            ]
        })[1]

        self.assertEquals(len(entity_tree.aliases), 1)
        self.assertEquals(entity_tree.aliases[0].name, 'ABC')
        self.assertEquals(entity_tree.aliases[0].sort_name, 'CBA')
        self.assertEquals(entity_tree.aliases[0].language_id, 1)
        self.assertEquals(entity_tree.annotation.content,
                          "Testing this entity, so don't actually use this.")
        self.assertEquals(entity_tree.disambiguation.comment,
                          "A disambiguation.")

    def test_update_entity_add_alias(self):
        query = db.session.query(EntityRevision).join(EntityTree)
        query = query.join(PublicationData).filter(
            PublicationData.entity_data_id is not None
        )

        test_entity = query.first().entity

        entity_tree = revision_json.parse_changes({
            'entity_gid': [test_entity.entity_gid],
            'aliases': [
                [None, {
                    'name': 'ABC',
                    'sort_name': 'CBA',
                    'language_id': 1,
                    'primary': True
                }]
            ]
        })[1]

        self.assertEquals(len(entity_tree.aliases), 5)
        self.assertEquals(entity_tree.aliases[-1].name, 'ABC')
        self.assertEquals(entity_tree.aliases[-1].sort_name, 'CBA')
        self.assertEquals(entity_tree.aliases[-1].language_id, 1)

    def test_update_entity_delete_alias(self):
        query = db.session.query(EntityRevision).join(EntityTree)
        query = query.join(PublicationData).filter(
            PublicationData.entity_data_id is not None
        )

        test_entity = query.first().entity

        entity_tree = revision_json.parse_changes({
            'entity_gid': [test_entity.entity_gid],
            'aliases': [
                [1, None],
                [2, None]
            ]
        })[1]

        self.assertEquals(len(entity_tree.aliases), 2)

    def test_update_entity_modify_alias(self):
        query = db.session.query(EntityRevision).join(EntityTree)
        query = query.join(PublicationData).filter(
            PublicationData.entity_data_id is not None
        )

        test_entity = query.first().entity

        entity_tree = revision_json.parse_changes({
            'entity_gid': [test_entity.entity_gid],
            'aliases': [
                [1, {
                    'name': 'Bob'
                }]
            ]
        })[1]

        self.assertEquals(len(entity_tree.aliases), 4)
        self.assertEquals(entity_tree.aliases[-1].name, 'Bob')

    def test_update_entity_update_attribs(self):
        query = db.session.query(EntityRevision).join(EntityTree)
        query = query.join(PublicationData).filter(
            PublicationData.entity_data_id is not None
        )

        test_entity = query.first().entity

        entity_tree = revision_json.parse_changes({
            'entity_gid': [test_entity.entity_gid],
            'annotation': 'Hello!',
            'disambiguation': 'Goodbye!'
        })[1]

        self.assertEquals(entity_tree.annotation.content, 'Hello!')
        self.assertEquals(entity_tree.disambiguation.comment, 'Goodbye!')

    def test_update_entity_update_data(self):
        query = db.session.query(EntityRevision).join(EntityTree)
        query = query.join(PublicationData).filter(
            PublicationData.entity_data_id is not None
        )

        test_entity = query.first().entity

        entity_tree = revision_json.parse_changes({
            'entity_gid': [test_entity.entity_gid],
            'publication_data': {
                'publication_type_id': 2
            }
        })[1]

        self.assertEquals(entity_tree.data.publication_type_id, 2)
