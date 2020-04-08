import graphene_sqlalchemy
import graphene
from application.models import WebsiteModel


class Website(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = WebsiteModel
        interfaces = (graphene.relay.Node,)