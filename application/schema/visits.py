from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from application.models import VisitModel


class Visit(SQLAlchemyObjectType):
    class Meta:
        model = VisitModel
        interfaces = (graphene.relay.Node,)
