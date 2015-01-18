# -*- coding: utf8 -*-

from bbschema import CreatorData, Edit, Entity, PublicationData, User, UserType, EntityTree, CreatorType, PublicationType, Alias, EntityRevision, Disambiguation


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

    entity1.master_revision = revision1
    entity2.master_revision = revision2
    entity3.master_revision = revision3
    db.session.add_all([revision1, revision2, revision3])
    db.session.commit()
