from bbschema import UserType


def load_data(db):
    editor_type = UserType(label=u'Editor')
    db.session.add(editor_type)

    db.session.commit()
