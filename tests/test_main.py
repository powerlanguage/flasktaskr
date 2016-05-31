import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class MainTests(unittest.TestCase):
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

    # helper methods

    def login(self, name, password):
        """Login Helper."""
        return self.app.post(
            '/',
            data=dict(name=name, password=password),
            follow_redirects=True
        )

    # tests

    def test_404_error(self):
        response = self.app.get('/this-route-doesnt-exist')
        self.assertEquals(response.status_code, 404)
        self.assertIn(b'Sorry, there\'s nothing here.', response.data)

    def test_500_error(self):
        bad_user = User(
            name='josh',
            email='assasd@ asdd',
            password='shouldnotbemanuallyset'
        )
        db.session.add(bad_user)
        db.session.commit()
        response = self.login('josh', 'shouldnotbemanuallyset')
        self.assertEquals(response.status_code, 500)
        self.assertNotIn(b'Value Error: Invalid salt', response.data)
        self.assertIn(b'Something went terrible wrong', response.data)

if __name__ == "__main__":
    unittest.main()
