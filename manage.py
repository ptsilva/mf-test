from flask.cli import FlaskGroup
import click
from wsgi import app
from application import db
from application.schema.schema import schema
from application.models import VisitModel
from graphql.utils import schema_printer
from sqlalchemy_utils import database_exists, create_database
from tests.base import WebsiteFactory, UserFactory
import random
import json
from graphene.test import Client

cli = FlaskGroup(app)


@cli.command('generate_schema')
def generate_schema():
    print('Generating schema...')
    my_schema_str = schema_printer.print_schema(schema)
    with open('schema.graphql', 'w') as f:
        f.write(my_schema_str)
    print('Done.')


@cli.command("create_db")
def create_db():
    if not database_exists(db.engine.url):
        create_database(db.engine.url)
    # db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command('db_seed')
def db_seed():
    print('Seeding...')
    websites = WebsiteFactory.create_batch(30)
    users = UserFactory.create_batch(30)
    all = []
    all.extend(websites)
    all.extend(users)
    db.session.add_all(all)
    db.session.commit()
    for i in range(25):
        visit = VisitModel(user_id=random.choice(users).id, website_id=random.choice(websites).id)
        db.session.add(visit)

    db.session.commit()
    print('Done.')


@cli.command('query')
@click.argument("query")
def query(query):
    string = json.dumps(Client(schema=schema).execute(query), sort_keys=False, indent=2)
    print(string)


if __name__ == "__main__":
    cli()
