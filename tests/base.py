import os
import factory
import unittest
from graphene.test import Client
from application import create_app, db
from application.schema.schema import schema
from application.models import UserModel, WebsiteModel
from typing import Dict, Any
from os import environ
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


class UserFactory(factory.Factory):
    class Meta:
        model = UserModel

    email = factory.Faker('ascii_email')
    name = factory.Faker('name')
    gender = 'MALE'
    date_of_birth = factory.Faker('past_date')


class WebsiteFactory(factory.Factory):
    class Meta:
        model = WebsiteModel

    url = factory.Faker('url')
    topic = factory.Faker('catch_phrase')


class BaseTest (unittest.TestCase):
    def setUp(self):

        db_uri = environ.get('TESTING_SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:123@localhost:5432/testing')
        engine = create_engine(db_uri)
        if not database_exists(engine.url):
            create_database(engine.url)

        self.app = create_app({'SQLALCHEMY_DATABASE_URI': db_uri})

        self.session = db.session
        self.client = Client(schema=schema)
        context = self.app.app_context()
        context.push()

        self.session.execute('delete from visits')
        self.session.execute('delete from users')
        self.session.execute('delete from websites')

    def tearDown(self) -> None:
        self.session.execute('delete from visits')
        self.session.execute('delete from users')
        self.session.execute('delete from websites')

    def assertDictValueEquals(self, path: str, target: Dict, expected: Any):
        try:
            value = None
            for segment in path.split('.'):
                value = target.get(segment, {})
            self.assertEqual(value, expected)
        except Exception:
            self.fail(msg=f'Fails assert dict has {path} with value {expected}')
