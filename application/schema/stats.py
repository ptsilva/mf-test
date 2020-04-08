import graphene
from application.schema.users import User
from application.schema.websites import Website
from application.schema.visits import Visit


class Stats(graphene.ObjectType):
    users_count = graphene.Int()
    websites_count = graphene.Int()
    visits_count = graphene.Int()
    users = graphene.List(User)
    websites = graphene.List(Website)
    visits = graphene.List(Visit)

    class Meta:
        interfaces = (graphene.relay.Node,)
