import logging

from bbschema import create_all, WorkData, Work, EntityRevision
from flask_testing import TestCase

from args_generators import *
from bbws import create_app, db
from check_helper_functions import *
from fixture import load_data


class TestDisplayAlias(TestCase):

    def create_app(self):
            self.app = create_app('../config/test.py')
            return self.app

    # noinspection PyPep8Naming
    def setUp(self):

        logging.basicConfig(level=logging.INFO)
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")
        db.engine.execute("CREATE SCHEMA bookbrainz")
        create_all(db.engine)

        random.seed()
        load_data(db)

    # noinspection PyPep8Naming
    def tearDown(self):
        db.session.remove()
        db.engine.execute("DROP SCHEMA IF EXISTS bookbrainz CASCADE")

    def test_display_alias(self):
        logging.info('Tests for display alias({})'
                     .format(TEST_DISPLAY_ALIASES_COUNT))
        for i in range(TEST_DISPLAY_ALIASES_COUNT):
            logging.info('Test {} for display_alias '.format(i+1))
            self.display_alias_single_test()

    def display_alias_single_test(self):
        """Tests if display_alias is correct in get/:id response

        @return: None
        """
        self.prepare_data()
        editor = sample_data_helper_functions._editor
        response = self.client.get(
            '/{}/{}/'.format('work', self.work.entity_gid),
            data={'user_id': editor.user_id}
        )
        self.assert200(response)
        data = response.json
        if 'display_alias' in data:
            da_json = data['display_alias']
            natives = [x.language_id for x in editor.languages
                       if x.proficiency == 'NATIVE']
            aliases = self.work_data.aliases
            primary = [x for x in aliases if x.primary is True]
            results = []

            def check():
                if results:
                    self.assertTrue(
                        self.json_alias_in_list(da_json, results)
                    )
                    return True
                return False

            results = [x for x in primary if x.language_id in natives]
            if check():
                return

            results = \
                [x for x in primary if x.language_id in
                    [y.id for y in self.work_data.languages]]
            if check():
                return

            english_languages = \
                set([y.id for y in db.session.query(Language).filter(
                    Language.name == 'English').all()])
            results = \
                [x for x in primary if x.language_id in english_languages]
            if check():
                return

            results = primary
            if check():
                return

            results = aliases
            if check():
                return
            self.assertEquals(da_json, None)

    def prepare_data(self):
        editor = sample_data_helper_functions._editor
        work_types = sample_data_helper_functions._work_types
        langs = sample_data_helper_functions._languages
        self.work = Work()
        self.work_data = \
            WorkData(**(get_work_data_args_generator(work_types, langs)()))

        db.session.add_all((self.work, self.work_data))
        db.session.commit()

        work_revision = \
            EntityRevision(
                user_id=sample_data_helper_functions._editor.user_id,
                entity_gid=self.work.entity_gid,
                entity_data_id=self.work_data.entity_data_id,
            )
        db.session.add(work_revision)
        self.work.master_revision = work_revision
        db.session.commit()

    def json_alias_in_list(self, json_alias, aliases):
        for alias in aliases:
            try:
                bbid_check_single_alias_json(self, json_alias, alias)
                return True
            except:
                pass
        return False


