from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from application.models import VisitModel
from application.schema.scalars import Url, Email


class Visit(SQLAlchemyObjectType):
    class Meta:
        model = VisitModel
        interfaces = (graphene.relay.Node,)


class NewVisit(graphene.Mutation):
    class Arguments:
        website_url = graphene.Field(Url)
        user_email = graphene.Field(Email)

    visit = graphene.Field(Visit)

    def mutate(self, info, website_url, user_email):
        pass