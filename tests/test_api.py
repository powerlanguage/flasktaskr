"""Flasktaskr api tests."""

import os
import unittest
from datetime import date

from project import app, db
from project._config import basedir
from project.models import Task

TEST_DB = 'test.db'


class APITests(unittest.TestCase):
    """Test Class."""

    # Setup and Teardown

    def setUp(self):
        """Set up."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        # Make sure we are testing in production mode

        self.assertEquals(app.debug, False)

    def tearDown(self):
        """Tear down."""
        db.session.remove()
        db.drop_all()

    # Helper Methods

    def add_tasks(self):
        """Add dummy tasks."""
        db.session.add(
            Task(
                "Test task 1.",
                date(2016, 10, 22),
                10,
                date(2016, 9, 12),
                1,
                1
            )
        )
        db.session.commit()

        db.session.add(
            Task(
                "A totally different thing.",
                date(2016, 1, 13),
                8,
                date(2016, 10, 24),
                1,
                1
            )
        )
        db.session.commit()

    # Tests

    def test_collection_endpoint_returns_correct_data(self):
        """Collection endpoint returns correct data."""
        self.add_tasks()
        response = self.app.get('api/v1/tasks/', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn(b'Test task 1.', response.data)
        self.assertIn(b'A totally different thing.', response.data)

    def test_resource_endpoint_returns_correct_data(self):
        """Resource endpoint returns correct data."""
        self.add_tasks()
        response = self.app.get('api/v1/tasks/2', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertNotIn(b'Test task 1.', response.data)
        self.assertIn(b'A totally different thing.', response.data)

    def test_invalid_resource_endpoint_returns_error(self):
        """Invalid endpoint returns error."""
        self.add_tasks()
        response = self.app.get('api/v1/tasks/209', follow_redirects=True)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn(b'Element does not exist', response.data)

if __name__ == "__main__":
    unittest.main()
