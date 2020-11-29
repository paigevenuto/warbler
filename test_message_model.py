"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

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


class MessageModelTestCase(TestCase):
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

    def test_basic_message_model(self):
        userone = User.query.filter_by(username="userone").first_or_404()
        msg = Message(text="Hello")
        userone.messages.append(msg)
        db.session.commit()
        messages = Message.query.all()
        self.assertEqual(len(messages), 1)

    def test_like_message(self):
        usertwo = User.query.filter_by(username="usertwo").first_or_404()
        msg = Message(text="Hello")
        usertwo.messages.append(msg)
        db.session.commit()
        message = Message.query.one()
        userone = User.query.filter_by(username="userone").first_or_404()
        userone.likes.append(message)
        db.session.commit()
        userone = User.query.filter_by(username="userone").first_or_404()
        testmsg = userone.likes[0]
        self.assertEqual(testmsg.text, "Hello")
