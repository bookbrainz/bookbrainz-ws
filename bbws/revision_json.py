import uuid
from . import db
from bbschema import (Entity, EntityTree, EntityRevision, PublicationData, CreatorData,
                      Annotation, Disambiguation, Alias)

class JSONParseError(Exception):
    pass


def create_entity(revision_json):
    # Make an entity
    entity = Entity()

    # Create the correct type of data
    if 'publication_data' in revision_json:
        data = PublicationData(**revision_json['publication_data'])
    elif 'creator_data' in revision_json:
        data = CreatorData(**revision_json['creator_data'])
    else:
        raise JSONParseError('Unrecognized entity type!')

    # Here, data will be valid, although not yet added to the database.
    # Create the entity tree, specifying the data in a relationship.
    entity_tree = EntityTree()
    entity_tree.data = data

    # Create any specified aliases, annotations or disambiguations
    if 'annotation' in revision_json:
        annotation = Annotation(content=revision_json['annotation'])
        entity_tree.annotation = annotation

    if 'disambiguation' in revision_json:
        disambiguation = Disambiguation(comment=revision_json['disambiguation'])
        entity_tree.disambiguation = disambiguation

    if 'aliases' in revision_json:
        for alias_json in revision_json['aliases']:
            alias = Alias(
                name=alias_json['name'], sort_name=alias_json['sort_name'],
                language_id=alias_json['language_id']
            )
            entity_tree.aliases.append(alias)

    return (entity, entity_tree)


def update_entity(revision_json):
    pass


def merge_entity(revision_json):
    pass


def delete_entity(revision_json):
    pass


def parse(revision_json):
    """Parses the recieved JSON and attempts to create a new revision using the
    specified changes.
    """

    # First, determine which type of edit this is.
    entity_gid = revision_json['entity_gid']
    if not entity_gid:
        # If entity_gid is empty, then this is a CREATE.
        return create_entity(revision_json)
    elif len(entity_gid) == 1:
        # Otherwise, if there is 1 element in entity_gid, attempt an update.
        return update_entity(revision_json)
    elif entity_gid[-1] is None:
        # If entity_gid[-1] is None, then this is a deletion.
        return delete_entity(revision_json)
    else:
        # If entity_gid[-1] is not None, then this is a merge.
        return merge_entity(revision_json)


def format(base_revision_id, new_revision_id):
    """This analyzes the changes from one revision to another, and formats
    them into a single JSON structure for serving through the webservice.
    """

    # This may throw a "NoResultsFound" exception.
    new_revision = \
        db.session.query(EntityRevision).filter_by(id=new_revision_id).one()

    new_tree = new_revision.entity_tree
    new_data = new_tree.data
    new_annotation = new_tree.annotation.content
    new_disambiguation = new_tree.disambiguation.comment
    new_aliases = new_tree.aliases

    if base_revision_id is None:
        base_data = None
        base_annotation = None
        base_disambiguation = None
        base_aliases = None
    else:
        base_revision = db.session.query(EntityRevision).filter_by(
            id=base_revision_id
        ).one()
        base_tree = base_revision.entity_tree

        base_data = base_tree.data
        base_annotation = (base_tree.annotation.content
                           if base_tree.annotation is not None else None)
        base_disambiguation = (base_tree.disambiguation.comment
                               if base_tree.disambiguation is not None else None)
        base_aliases = base_tree.aliases

    return {
        'data': [base_data, new_data],
        'annotation': [base_annotation, new_annotation],
        'disambiguation': [base_disambiguation, new_disambiguation],
        'aliases': [base_aliases, new_aliases]
    }
