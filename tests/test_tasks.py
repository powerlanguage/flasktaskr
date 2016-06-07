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

    def create_admin_user(self, name, email, password):
        """Direct create an admin user."""
        new_admin = User(
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(password),
            role='admin'
        )
        db.session.add(new_admin)
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

    def test_logged_in_users_can_access_tasks_page(self):
        """Logged in users can access tasks page."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        response = self.app.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Save new task', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        """Logged out users cannot access tasks page."""
        response = self.app.get('/tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first', response.data)

    def test_users_can_add_tasks(self):
        """User can add tasks."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        response = self.create_task()
        self.assertIn(b'was successfully posted. Thanks.', response.data)

    def test_users_cannot_add_tasks_when_error(self):
        """Adding tasks with blank field errors."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        response = self.app.post(
            'add/',
            data=dict(
                name='Goto the bank',
                due_date='',
                priority='1',
                posted_date='02/04/2014',
                status=1
            ),
            follow_redirects=True
        )
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        """User can complete tasks."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        response = self.app.get('/complete/1/', follow_redirects=True)
        self.assertIn(b'was completed. Nice', response.data)

    def test_users_can_delete_tasks(self):
        """User can delete tasks."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        response = self.app.get('/delete/1/', follow_redirects=True)
        self.assertIn(b'was deleted. Nice', response.data)

    def test_users_cannot_complete_tasks_created_by_other(self):
        """User cannot complete tasks created by other."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        self.logout()
        self.register("joshua", "josh@ua.com", "joshua", "joshua")
        self.login('joshua', 'joshua')
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertNotIn(b'was completed. Nice', response.data)
        self.assertIn(
            b'You can only update tasks that belong to you.',
            response.data
        )

    def test_users_cannot_delete_tasks_created_by_other(self):
        """User cannot delete tasks created by other."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        self.logout()
        self.register("joshua", "josh@ua.com", "joshua", "joshua")
        self.login('joshua', 'joshua')
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertNotIn(b'was deleted. Nice', response.data)
        self.assertIn(
            b'You can only delete tasks that belong to you.',
            response.data
        )

    def test_admin_users_can_complete_tasks_created_by_other(self):
        """Admin can complete any task."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        self.logout()
        self.create_admin_user("joshua", "josh@ua.com", "joshua")
        self.login('joshua', 'joshua')
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn(b'was completed. Nice', response.data)

    def test_admin_users_can_delete_tasks_created_by_other(self):
        """Admin can delete any task."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        self.logout()
        self.create_admin_user("joshua", "josh@ua.com", "joshua")
        self.login('joshua', 'joshua')
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn(b'was deleted. Nice', response.data)

    def test_task_template_displays_logged_in_user_name(self):
        """Template displays logged in user name."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'tonyhat', response.data)

    def test_users_cannot_see_task_modify_links_for_other_tasks(self):
        """User cannot see task modify links for other user tasks."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        self.create_task()
        self.app.get('complete/2/')
        self.logout()
        self.register("joshua", "josh@ua.com", "joshua", "joshua")
        self.login('joshua', 'joshua')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertNotIn(b'Complete', response.data)
        self.assertNotIn(b'Delete', response.data)

    def test_users_can_see_task_modify_links_for_own_tasks(self):
        """User can see task modify links for own tasks."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        self.logout()
        self.register("joshua", "josh@ua.com", "joshua", "joshua")
        self.login('joshua', 'joshua')
        self.create_task()
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'/complete/2/', response.data)
        self.assertIn(b'/delete/2/', response.data)

    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        """Admin can see all task modify links."""
        self.register("tonyhat", "tony@hat.com", "tonyhat", "tonyhat")
        self.login('tonyhat', 'tonyhat')
        self.create_task()
        self.logout()
        self.create_admin_user("joshua", "josh@ua.com", "joshua")
        self.login('joshua', 'joshua')
        self.create_task()
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'/complete/1/', response.data)
        self.assertIn(b'/delete/1/', response.data)
        self.assertIn(b'/complete/2/', response.data)
        self.assertIn(b'/delete/2/', response.data)

if __name__ == "__main__":
    unittest.main()
