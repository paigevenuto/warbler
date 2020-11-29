"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.seconduser = User.signup(username="seconduser",
                                    email="second@test.com",
                                    password="password",
                                    image_url=None)

        db.session.commit()

    def test_follower_list(self):
        testuser = User.query.filter_by(username="testuser").first_or_404()
        seconduser = User.query.filter_by(username="seconduser").first_or_404()
        seconduser.following.append(testuser)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)
            self.assertIn("seconduser", html)

    def test_following_list(self):
        seconduser = User.query.filter_by(username="seconduser").first_or_404()
        testuser = User.query.filter_by(username="testuser").first_or_404()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            test = c.post(f"/users/follow/{seconduser.id}", follow_redirects=True)
            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)
            self.assertIn("seconduser", html)

    def test_anon_followers(self):
        seconduser = User.query.filter_by(username="seconduser").first_or_404()
        testuser = User.query.filter_by(username="testuser").first_or_404()

        with self.client as c:
            with c.session_transaction() as sess:
                sess.clear()
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)

    def test_anon_following(self):
        seconduser = User.query.filter_by(username="seconduser").first_or_404()
        testuser = User.query.filter_by(username="testuser").first_or_404()

        with self.client as c:
            with c.session_transaction() as sess:
                sess.clear()
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("Access unauthorized.", html)
    
