import graphene


class Email(graphene.String):
    pass


class Url(graphene.String):
    pass


class Timestamp(graphene.DateTime):
    pass


class Topic(graphene.String):
    pass
