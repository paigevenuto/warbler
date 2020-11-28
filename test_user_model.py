"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from psycopg2 import errors
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        user1 = User(
        email="one@one.com",
        username="userone",
        password="HASHED_PASSWORD"
        )

        user2 = User(
        email="two@two.com",
        username="usertwo",
        password="HASHED_PASSWORD"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_following(self):
        user1 = User.query.filter_by(username="userone").first_or_404()
        user2 = User.query.filter_by(username="usertwo").first_or_404()

        user1.following.append(user2)
        db.session.commit()
        self.assertIn(user2, user1.following)
        self.assertTrue(user1.is_following(user2))

    def test_is_not_following(self):
        user1 = User.query.filter_by(username="userone").first_or_404()
        user2 = User.query.filter_by(username="usertwo").first_or_404()

        self.assertNotIn(user2, user1.following)
        self.assertFalse(user1.is_following(user2))

    def test_is_followed_by(self):
        user1 = User.query.filter_by(username="userone").first_or_404()
        user2 = User.query.filter_by(username="usertwo").first_or_404()

        user1.following.append(user2)
        db.session.commit()
        self.assertIn(user1, user2.followers)
        self.assertTrue(user2.is_followed_by(user1))

    def test_is_not_followed_by(self):
        user1 = User.query.filter_by(username="userone").first_or_404()
        user2 = User.query.filter_by(username="usertwo").first_or_404()

        self.assertNotIn(user1, user2.followers)
        self.assertFalse(user2.is_followed_by(user1))

    def test_signup(self):
        User.signup(
            email="test@test.com",
            username="test",
            password="password",
            image_url=None
        )
        success = User.query.filter_by(username="test").first_or_404()
        self.assertTrue(success)


    def test_blank_signup(self):
        User.signup(
            email=None,
            username=None,
            password="HASHED_PASSWORD",
            image_url=None
        )
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

        db.session.rollback()

    def test_auth(self):
        User.signup(
            email="test@test.com",
            username="test",
            password="password",
            image_url=None
        )
        success = User.authenticate('test', 'password')
        self.assertTrue(success)

    def test_auth_pass_fail(self):
        User.signup(
            email="test@test.com",
            username="test",
            password="password",
            image_url=None
        )
        success = User.authenticate('test', 'asdfasfhasdjfhasd')
        self.assertFalse(success)

    def test_auth_name_fail(self):
        User.signup(
            email="test@test.com",
            username="test",
            password="password",
            image_url=None
        )
        success = User.authenticate('asdjfhajlsdkfhasjlkdfh', 'password')
        self.assertFalse(success)
