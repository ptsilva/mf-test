from application.services import users, websites, visits
from application.schema.users import User
from application.schema.websites import Website
from application.schema.visits import Visit
from application.schema import scalars
import graphene


class UpsertUser(graphene.Mutation):
    class Arguments:
        email = graphene.Argument(scalars.Email)
        name = graphene.String()
        gender = graphene.String()
        date_of_birth = graphene.Date()

    user = graphene.Field(User)

    def mutate(self, info, **kwargs):
        user = users.upsert_user(kwargs)
        return UpsertUser(user=user)


class UpsertWebsite(graphene.Mutation):
    class Arguments:
        url = graphene.Argument(scalars.Url)
        topic = graphene.Argument(scalars.Topic)

    website = graphene.Field(Website)

    def mutate(self, info, **kwargs):
        website = websites.upsert_website(kwargs)
        return UpsertWebsite(website=website)


class NewVisit(graphene.Mutation):
    class Arguments:
        url = graphene.Argument(scalars.Url)
        email = graphene.Argument(scalars.Email)

    visit = graphene.Field(Visit)

    def mutate(self, info, **kwargs):
        visit = visits.new_visit(info, **kwargs)
        return NewVisit(visit=visit)
