from application.schema.users import User
from application.models import UserModel, VisitModel, WebsiteModel
# from application.utils import model2dict
from application import db
from sqlalchemy import asc, desc, func, distinct
from typing import List, Dict
from datetime import datetime
from application.utils import apply_filters
import graphene
from collections import defaultdict


def get_user_by_id(info: graphene.ResolveInfo, id: int) -> User:
    """Filter user by id"""
    return User.get_query(info).get(id)


def get_user_by_email(info: graphene.ResolveInfo, email: str) -> User:
    """Filter user by email"""
    return User.get_query(info).filter_by(email=email).first()


def get_users_by_emails(info: graphene.ResolveInfo, emails: List) -> List[User]:
    """"Filters user by list of emails"""
    return User.get_query(info).filter(UserModel.email.in_(emails)).all()


def get_users(info: graphene.ResolveInfo, limit: int, skip: int, sort_field: str, sort_order: str) -> List[User]:
    """Get users with some slicing control"""
    if sort_field and sort_order:
        sort = desc(sort_field) if sort_order == 'desc' else asc(sort_field)
    else:
        sort = asc('id')

    query = User.get_query(info).order_by(sort).limit(limit).offset(skip)

    return query.all()


def get_by_timestamps_visit(initial: datetime = None, final: datetime = None) -> List:
    """Returns users filtered by timestamps"""
    query = db.session.query(UserModel).join(VisitModel)

    if initial:
        query = query.filter(VisitModel.timestamp >= initial)

    if final:
        query = query.filter(VisitModel.timestamp <= final)

    return query.all()


def get_count_users_by_websites(filters: dict) -> Dict:
    """Get count aggregation of users by websites"""
    query = db.session.query(UserModel)

    vists_on = VisitModel.user_id == UserModel.id
    query = apply_filters(query, filters).join(VisitModel, vists_on).join(WebsiteModel)

    query = query.with_entities(WebsiteModel.id, func.count(UserModel.id)).group_by(WebsiteModel.id)

    count = query.all()

    result = defaultdict(int)

    for user in count:
        user = dict(zip(['website_id', 'count'], user))
        result[user.get('website_id')] = user.get('count')

    return result


def get_count_by_timestamps(**filters):
    """Return count of users filtered by timestamp range"""
    query = apply_filters(db.session.query(VisitModel), filters).join(UserModel).distinct(UserModel.id)

    return query.count()


def get_users_by_websites(filters: dict) -> Dict:
    """Returns users grouped by websites"""
    columns = [
        UserModel.id,
        UserModel.name,
        UserModel.email,
        UserModel.date_of_birth,
        UserModel.gender,
        WebsiteModel.id.label('website_id')
    ]

    query = db.session.query(*columns)

    vists_on = VisitModel.user_id == UserModel.id
    query = apply_filters(query, filters).join(VisitModel, vists_on).join(WebsiteModel)

    columns_names = [col.key for col in columns]

    result = defaultdict(list)

    for user in query.all():
        row = dict(zip(columns_names, user))
        website_id = row.get('website_id')
        del row['website_id']
        user = UserModel(**row)
        result[website_id].append(user)

    return result
