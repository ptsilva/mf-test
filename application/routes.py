from flask import current_app as app
from flask_graphql import GraphQLView
from application.schema.schema import schema
from application import db
from application.models import UserModel, WebsiteModel, VisitModel, Gender
from datetime import datetime, date, timedelta

app.add_url_rule(
    '/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

