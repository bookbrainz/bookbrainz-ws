# -*- coding: utf8 -*-

from bbschema import (Alias, CreatorData, CreatorType, Disambiguation, Edit,
                      Entity, EntityRevision, EntityTree, PublicationData,
                      PublicationType, Relationship, RelationshipEntity,
                      RelationshipRevision, RelationshipText, RelationshipTree,
                      RelationshipType, User, UserType)


def load_data(db):
    editor_type = UserType(label=u'Editor')
    db.session.add(editor_type)
    db.session.commit()

    editor = User(name=u'Bob', email=u'bob@bobville.org',
                  user_type_id=editor_type.id)
    db.session.add(editor)

    pub_type = PublicationType(label=u'Book')
    pub_type2 = PublicationType(label=u'Magazine')
    db.session.add_all((pub_type, pub_type2))
    db.session.commit()

    creator_type = CreatorType(label=u'Author')
    db.session.add(creator_type)
    db.session.commit()

    edit1 = Edit(user_id=editor.id, status=0)
    edit2 = Edit(user_id=editor.id, status=0)
    db.session.add_all((edit1, edit2))
    db.session.commit()

    entity1 = Entity()
    entity2 = Entity()
    entity3 = Entity()
    db.session.add_all((entity1, entity2, entity3))
    db.session.commit()

    pub_data1 = PublicationData(publication_type_id=pub_type.id)
    pub_data2 = PublicationData(publication_type_id=pub_type.id)
    creator_data = CreatorData(creator_type_id=creator_type.id)
    db.session.add_all([pub_data1, pub_data2, creator_data])

    entity_tree1 = EntityTree()
    entity_tree1.data = pub_data1
    entity_tree2 = EntityTree()
    entity_tree2.data = pub_data2
    entity_tree3 = EntityTree()
    entity_tree3.data = creator_data

    entity1_alias1 = Alias(name=u'アウト', sort_name=u'アウト')
    entity1_alias2 = Alias(name=u'Out', sort_name=u'Out')
    entity1_alias3 = Alias(name=u'Le quattro casalinghe di Tokyo', sort_name=u'Le quattro casalinghe di Tokyo')
    entity1_alias4 = Alias(name=u'De nachtploeg', sort_name=u'De nachtploeg')
    entity_tree1.aliases.extend([entity1_alias1, entity1_alias2, entity1_alias3, entity1_alias4])

    entity2_alias1 = Alias(name=u'桐野 夏生', sort_name=u'桐野 夏生')
    entity2_alias2 = Alias(name=u'Natsuo Kirino', sort_name=u'Kirino, Natsuo')
    entity_tree2.aliases.extend([entity2_alias1, entity2_alias2])

    entity3_alias1 = Alias(name=u'Stephen Snyder', sort_name=u'Snyder, Stephen')
    entity_tree3.aliases.append(entity3_alias1)

    entity1_disambig = Disambiguation(comment=u'book by Natsuo Kirino')
    entity_tree1.disambiguation = entity1_disambig

    db.session.add_all([entity_tree1, entity_tree2, entity_tree3])
    db.session.commit()

    revision1 = EntityRevision(user_id=editor.id, entity_gid=entity1.gid,
                               entity_tree_id=entity_tree1.id)
    revision2 = EntityRevision(user_id=editor.id, entity_gid=entity2.gid,
                               entity_tree_id=entity_tree2.id)
    revision3 = EntityRevision(user_id=editor.id, entity_gid=entity3.gid,
                               entity_tree_id=entity_tree3.id)

    revision1.edits = [edit1]
    revision2.edits = [edit1]
    revision3.edits = [edit2]

    relationship_type1 = RelationshipType(
        label='First Relationship',
        description='A relationship which is first.',
        forward_template='<%= subjects[0] %> is authored by <%= subjects[1] %>',
        reverse_template='<%= subjects[1] %> is the author of <%= subjects[0] %>',
    )

    relationship_type2 = RelationshipType(
        label='Second Relationship',
        description='A relationship which is second.',
        forward_template='<%= subjects[0] %> is translated by <%= subjects[1] %>',
        reverse_template='<%= subjects[1] %> is the translator of <%= subjects[0] %>',
    )

    relationship_type3 = RelationshipType(
        label='Third Relationship',
        description='A relationship which is third.',
        forward_template='<%= subjects[0] %> has profession <%= subjects[1] %>',
        reverse_template='<%= subjects[1] %> is the profession of <%= subjects[0] %>',
    )
    db.session.add_all((relationship_type1, relationship_type2, relationship_type3))
    db.session.commit()

    relationship1 = Relationship()
    relationship2 = Relationship()
    relationship3 = Relationship()
    db.session.add_all((relationship1, relationship2, relationship3))
    db.session.commit()

    relationship_tree1 = RelationshipTree(relationship_type_id=relationship_type1.id)
    relationship_tree1.entities = [
        RelationshipEntity(entity_gid=entity1.gid, position=1),
        RelationshipEntity(entity_gid=entity2.gid, position=2)
    ]
    relationship_tree2 = RelationshipTree(relationship_type_id=relationship_type2.id)
    relationship_tree2.entities = [
        RelationshipEntity(entity_gid=entity1.gid, position=1),
        RelationshipEntity(entity_gid=entity3.gid, position=2)
    ]
    relationship_tree3 = RelationshipTree(relationship_type_id=relationship_type3.id)
    relationship_tree3.entities = [
        RelationshipEntity(entity_gid=entity3.gid, position=1),
    ]
    relationship_tree3.text = [
        RelationshipText(text='translator', position=2),
    ]

    db.session.add_all([relationship_tree1, relationship_tree2, relationship_tree3])
    db.session.commit()

    revision4 = RelationshipRevision(
        user_id=editor.id, relationship_id=relationship1.id,
        relationship_tree_id=relationship_tree1.id
    )

    revision5 = RelationshipRevision(
        user_id=editor.id, relationship_id=relationship2.id,
        relationship_tree_id=relationship_tree2.id
    )

    revision6 = RelationshipRevision(
        user_id=editor.id, relationship_id=relationship3.id,
        relationship_tree_id=relationship_tree3.id
    )

    revision4.edits = [edit1]
    revision5.edits = [edit2]
    revision6.edits = [edit2]

    entity1.master_revision = revision1
    entity2.master_revision = revision2
    entity3.master_revision = revision3
    relationship1.master_revision = revision4
    relationship2.master_revision = revision5
    relationship3.master_revision = revision6

    db.session.add_all([revision1, revision2, revision3, revision4, revision5,
                        revision6])
    db.session.commit()
