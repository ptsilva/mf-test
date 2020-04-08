from application.schema import users, websites, stats, visits, scalars
from application.resolvers import users as users_resolver
from application.resolvers import websites as websites_resolver
from application.resolvers import stats as stats_resolver
from application.schema import scalars
import graphene


def pagination(model, resolver):
    return graphene.List(
        model,
        limit=graphene.Int(),
        skip=graphene.Int(),
        sort_field=graphene.String(),
        sort_order=graphene.String(),
        resolver=resolver
    )


class Query(graphene.ObjectType):
    user = graphene.Field(users.User, id=graphene.ID(), resolver=users_resolver.resolve_user_by_id)
    user_by_email = graphene.Field(users.User, email=scalars.Email(), resolver=users_resolver.resolve_user_by_email)
    users = pagination(users.User, resolver=users_resolver.resolve_users)

    website = graphene.Field(websites.Website, id=graphene.ID(), resolver=websites_resolver.resolve_website_by_id)
    website_by_url = graphene.Field(
        websites.Website, url=scalars.Url(), resolver=websites_resolver.resolve_website_by_url
    )
    websites = pagination(websites.Website, resolver=websites_resolver.resolve_websites)

    stats_total = graphene.Field(
        stats.Stats,
        initial_timestamp=graphene.DateTime(),
        final_timestamp=graphene.DateTime(),
        resolver=stats_resolver.resolve_stats_total
    )

    stats_by_website = graphene.List(
        stats.Stats,
        initial_timestamp=graphene.DateTime(),
        final_timestamp=graphene.DateTime(),
        min_age=graphene.Int(),
        max_age=graphene.Int(),
        gender=graphene.String(),
        users=graphene.List(scalars.Email),
        websites=graphene.List(scalars.Url),
        resolver=stats_resolver.resolve_stats_by_website
    )

    stats_by_user = graphene.List(
        stats.Stats,
        initial_timestamp=graphene.DateTime(),
        final_timestamp=graphene.DateTime(),
        min_age=graphene.Int(),
        max_age=graphene.Int(),
        gender=graphene.String(),
        users=graphene.List(scalars.Email),
        websites=graphene.List(scalars.Url),
        resolver=stats_resolver.resolve_stats_by_user
    )


schema = graphene.Schema(query=Query)
