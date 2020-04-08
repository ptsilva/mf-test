import graphene
from application.schema.stats import Stats
from application.models import VisitModel, WebsiteModel, UserModel
from application import db
from application.schema.users import User
from application.services import users as users_service, websites as websites_service, visits as visits_service
from datetime import datetime
from application.utils import apply_filters
from typing import List, Dict
from sqlalchemy import asc
from collections import defaultdict


def get_stats_total(info, initial_timestamp: datetime = None, final_timestamp: datetime = None) -> Stats:
    """Summarize stats of visits, users and websites"""
    visits_count = visits_service.get_count_visits_by_timestamps(
        initial_timestamp, final_timestamp
    )

    websites_count = websites_service.get_count_by_timestamps(
        initial_timestamp=initial_timestamp, final_timestamp=final_timestamp
    )
    users_count = users_service.get_count_by_timestamps(
        initial_timestamp=initial_timestamp, final_timestamp=final_timestamp
    )

    websites_list = websites_service.get_by_timestamps_visit(initial=initial_timestamp, final=final_timestamp)
    users_list = users_service.get_by_timestamps_visit(initial=initial_timestamp, final=final_timestamp)
    visits_list = visits_service.get_by_timestamps(initial=initial_timestamp, final=final_timestamp)

    return Stats(
        visits_count=visits_count,
        websites_count=websites_count,
        users_count=users_count,
        websites=websites_list,
        users=users_list,
        visits=visits_list
    )


def get_stats_by_website(info: graphene.ResolveInfo, filters: Dict) -> List[Stats]:
    """Get all stats fetching data with ONE HIT aggregation by website and restructure to return list of stats"""
    query = apply_filters(db.session.query(WebsiteModel), filters).join(VisitModel).join(UserModel)
    websites = query.order_by(asc(WebsiteModel.id)).distinct(WebsiteModel.id).all()

    users_count = users_service.get_count_users_by_websites(filters)
    users = users_service.get_users_by_websites(filters)

    visits_count = visits_service.get_count_visits_by_websites(filters)
    visits = visits_service.get_visits_by_websites(filters)

    stats_list = []

    for website in websites:
        stats_list.append(Stats(
            users_count=users_count[website.id],
            visits_count=visits_count[website.id],
            websites_count=1,
            websites=[website],
            users=users[website.id],
            visits=visits[website.id],
        ))

    return stats_list


def get_stats_by_user(info: graphene.ResolveInfo, filters: Dict):
    """Get all stats fetching data with aggregation by user and restructure to return list of stats"""

    query = apply_filters(db.session.query(UserModel), filters)
    users = query.join(VisitModel).join(WebsiteModel).order_by(asc(UserModel.id)).distinct(UserModel.id).all()

    websites_count = websites_service.get_count_websites_by_users(filters)
    websites = websites_service.get_websites_by_users(filters)

    visits_count = visits_service.get_count_visits_by_users(filters)
    visits = visits_service.get_visits_by_users(filters)

    stats_list = []

    for user in users:
        stats_list.append(Stats(
            users_count=1,
            visits_count=visits_count[user.id],
            websites_count=websites_count[user.id],
            websites=websites[user.id],
            users=[user],
            visits=visits[user.id],
        ))

    return stats_list

