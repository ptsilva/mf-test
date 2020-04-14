import graphene_sqlalchemy
import graphene
from application.models import UserModel


class User(graphene_sqlalchemy.SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (graphene.Node,)


