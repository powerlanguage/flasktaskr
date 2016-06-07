"""FlaskTaskr User Tests."""

import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class TestCase(unittest.TestCase):
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

    def register(self, name, email, password, confirm):
        """Register Helper."""
        return self.app.post(
            'register/',
            data=dict(
                name=name,
                email=email,
                password=password,
                confirm=confirm
            ),
            follow_redirects=True
        )

    def logout(self):
        """Logout Helper."""
        return self.app.get('logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        """Direct user create helper."""
        new_user = User(
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        """Fixed create task helper."""
        return self.app.post(
            'add/',
            data=dict(
                name='Goto the bank',
                due_date='02/05/2014',
                priority='1',
                posted_date='02/04/2014',
                status=1
            ),
            follow_redirects=True
        )

    # tests

    def test_form_is_present_on_login_page(self):
        """Login form present on login page."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please login', response.data)

    def test_users_cannot_login_unless_registered(self):
        """User cannot login unless registered."""
        response = self.login('asds', 'asdas')
        self.assertIn(
            b'Error: Invalid credentials.  Please try again.',
            response.data
        )

    def test_users_can_register(self):
        """User can register."""
        response = self.register(
            "tonyhat",
            "tony@hat.com",
            "tonyhat",
            "tonyhat"
        )
        self.assertIn(b'Thanks for registering,', response.data)

    def test_duplicate_user_registration_error(self):
        """Duplicate registration errors."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        response = self.register(
            "tonyhat",
            "tony@hat.com",
            "tonyhat",
            "tonyhat"
        )
        self.assertIn(
            b'That username and/or email already exists.',
            response.data
        )

    def test_users_can_login(self):
        """User can login."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        response = self.login('tonyhat', 'tonyhat')
        self.assertIn(b'Welcome', response.data)

    def test_invalid_form_data(self):
        """Login form errors on invalid data."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        response = self.login('alert("alert box!;', 'foo')
        self.assertIn(b'Invalid credentials', response.data)

    def test_form_is_present_on_register_page(self):
        """Register form present on register page."""
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please create an account', response.data)

    def test_logged_in_users_can_logout(self):
        """Logged in users can log out."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        response = self.logout()
        self.assertIn(b'Peace', response.data)

    def test_logged_out_users_cannot_logout(self):
        """Logged out user cannot log out."""
        response = self.logout()
        self.assertNotIn(b'Peace', response.data)

    def test_string_representation_of_user_object(self):
        """String representation of user object."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.name, "tonyhat")

    def test_default_user_role(self):
        """Default user role is user."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.role, "user")

if __name__ == "__main__":
    unittest.main()
