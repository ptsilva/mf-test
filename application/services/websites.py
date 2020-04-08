from application.schema.websites import Website
from application.models import WebsiteModel, VisitModel, UserModel
from application.utils import apply_filters
from application import db
# from application.utils import model2dict
from sqlalchemy import asc, desc, func
import graphene
from datetime import datetime
from typing import List, Dict
from collections import defaultdict


def get_website_by_id(info: graphene.ResolveInfo, id: int) -> Website:
    """Return website filtered by id"""
    return Website.get_query(info).get(id)


def get_website_by_url(info: graphene.ResolveInfo, url: str) -> Website:
    """Return webiste filtered by url"""
    return Website.get_query(info).filter_by(url=url).first()


def get_websites(info: graphene.ResolveInfo, limit: int, skip: int, sort_field: str, sort_order: str) -> List[WebsiteModel]:
    """Get websites using limit, skip, sort_field and sort_order"""
    if sort_field and sort_order:
        sort = desc(sort_field) if sort_order == 'desc' else asc(sort_field)
    else:
        sort = asc('id')

    query = Website.get_query(info).order_by(sort).limit(limit).offset(skip)

    return query.all()


def get_count_by_timestamps(**filters):
    """ Get count metric over websites by timestamp"""
    count = apply_filters(db.session.query(VisitModel), filters).join(WebsiteModel).distinct(WebsiteModel.id).count()
    return count


def get_by_timestamps_visit(initial: datetime = None, final: datetime = None) -> List[WebsiteModel]:
    """Return websites filtered by tiemstamps"""
    query = db.session.query(WebsiteModel).join(VisitModel)

    if initial:
        query = query.filter(VisitModel.timestamp >= initial)

    if final:
        query = query.filter(VisitModel.timestamp <= final)

    return query.all()


def get_count_websites_by_users(filters: dict) -> Dict:
    """"Returns count metric of websites with group by user"""
    query = db.session.query(UserModel)

    vists_on = VisitModel.user_id == WebsiteModel.id
    query = apply_filters(query, filters).join(VisitModel).join(WebsiteModel)

    query = query.with_entities(UserModel.id, func.count(WebsiteModel.id)).group_by(UserModel.id)

    count = query.all()

    result = defaultdict(int)

    for website in count:
        website = dict(zip(['user_id', 'count'], website))
        result[website.get('user_id')] = website.get('count')

    return result


def get_websites_by_users(filters: dict) -> Dict:
    """Returns websites grouped by users"""
    columns = [
        WebsiteModel.id,
        WebsiteModel.url,
        WebsiteModel.topic,
        UserModel.id.label('user_id')
    ]

    query = db.session.query(*columns)

    visits_on = VisitModel.website_id == WebsiteModel.id
    query = apply_filters(query, filters).join(VisitModel, visits_on).join(UserModel)

    columns_names = [col.key for col in columns]

    result = defaultdict(list)

    for website in query.all():
        row = dict(zip(columns_names, website))
        user_id = row.get('user_id')
        del row['user_id']
        website = WebsiteModel(**row)
        result[user_id].append(website)

    return result
