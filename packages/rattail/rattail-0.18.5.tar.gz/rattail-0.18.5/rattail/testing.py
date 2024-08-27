# -*- coding: utf-8; -*-

from wuttjamaican.testing import FileConfigTestCase
from rattail.config import RattailConfig


class DataTestCase(FileConfigTestCase):
    """
    Base class for test suites requiring a full (typical) database.
    """

    def setUp(self):
        self.setup_db()

    def setup_db(self):
        self.setup_files()
        self.config = self.make_config()
        self.app = self.config.get_app()

        # init db
        model = self.app.model
        model.Base.metadata.create_all(bind=self.config.appdb_engine)
        self.session = self.app.make_session()

    def tearDown(self):
        self.teardown_db()

    def teardown_db(self):
        self.teardown_files()

    def make_config(self):
        return RattailConfig(defaults={
            'rattail.db.default.url': 'sqlite://',
        })
