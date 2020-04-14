from application.models import VisitModel, WebsiteModel, UserModel
from application.schema.visits import Visit
from application.utils import apply_filters, get_or_create, model2dict
from collections import defaultdict
from datetime import datetime
from typing import List, Dict
from sqlalchemy import func
from application import db


def get_count_visits_by_timestamps(initial: datetime = None, final: datetime = None) -> int:
    """Get total of visits filtered by timestamps range"""
    filters = {
        'initial_timestamp': initial,
        'final_timestamp': final
    }

    query = apply_filters(db.session.query(VisitModel), filters)

    return query.count()


def get_by_timestamps(initial: datetime = None, final: datetime = None) -> List:
    """Return rows of visits filtered by timestamps range"""
    query = db.session.query(VisitModel)

    if initial:
        query = query.filter(VisitModel.timestamp >= initial)

    if final:
        query = query.filter(VisitModel.timestamp <= final)

    return query.all()


def get_visits_by_websites(filters) -> Dict:
    """Returns rows of visits grouped by websites"""
    columns = [
        VisitModel.id,
        VisitModel.website_id,
        VisitModel.user_id,
        VisitModel.timestamp,
        WebsiteModel.url,
        WebsiteModel.topic,
        UserModel.name,
        UserModel.email,
        UserModel.date_of_birth,
        UserModel.gender
    ]

    query = db.session.query(*columns)

    users_on = VisitModel.user_id == UserModel.id
    query = apply_filters(query, filters).join(UserModel, users_on).join(WebsiteModel)

    columns_names = [col.key for col in columns]
    visits = [dict(zip(columns_names, row)) for row in query.all()]

    result = defaultdict(list)

    for visit in visits:
        website = WebsiteModel(id=visit.get('website_id'), url=visit.get('url'), topic=visit.get('topic'))
        user = UserModel(
            id=visit.get('user_id'),
            name=visit.get('name'),
            email=visit.get('email'),
            gender=visit.get('gender'),
            date_of_birth=visit.get('date_of_birth')
        )
        object_visit = VisitModel(
            id=visit.get('id'),
            user=user,
            website=website,
            timestamp=visit.get('timestamp')
        )

        result[visit.get('website_id')].append(object_visit)

    return result


def get_count_visits_by_websites(filters) -> Dict:
    """ Return count of visits grouped by websites"""
    query = apply_filters(db.session.query(VisitModel), filters)
    query = query.join(WebsiteModel).join(UserModel)

    query = query.with_entities(
        WebsiteModel.id, func.count(VisitModel.id)
    ).group_by(WebsiteModel.id)

    result = defaultdict(int)

    count_group = query.all()
    for visit in count_group:
        visit = dict(zip(['website_id', 'count'], visit))
        result[visit.get('website_id')] = visit.get('count')

    return result


def get_visits_by_users(filters) -> Dict:
    """ Get visits grouped by users applying others filters"""
    columns = [
        VisitModel.id,
        VisitModel.website_id,
        VisitModel.user_id,
        VisitModel.timestamp,
        WebsiteModel.url,
        WebsiteModel.topic,
        UserModel.name,
        UserModel.email,
        UserModel.date_of_birth,
        UserModel.gender
    ]

    query = db.session.query(*columns)

    users_on = VisitModel.user_id == UserModel.id
    query = apply_filters(query, filters).join(UserModel, users_on).join(WebsiteModel)

    columns_names = [col.key for col in columns]
    visits = [dict(zip(columns_names, row)) for row in query.all()]

    result = defaultdict(list)

    for visit in visits:
        website = WebsiteModel(id=visit.get('website_id'), url=visit.get('url'), topic=visit.get('topic'))
        user = UserModel(
            id=visit.get('user_id'),
            name=visit.get('name'),
            email=visit.get('email'),
            gender=visit.get('gender'),
            date_of_birth=visit.get('date_of_birth')
        )
        object_visit = VisitModel(
            id=visit.get('id'),
            user=user,
            website=website,
            timestamp=visit.get('timestamp')
        )

        result[visit.get('user_id')].append(object_visit)

    return result


def get_count_visits_by_users(filters) -> Dict:
    """Get count of visits grouped by users"""
    query = apply_filters(db.session.query(VisitModel), filters)
    query = query.join(WebsiteModel).join(UserModel)

    query = query.with_entities(
        UserModel.id, func.count(VisitModel.id)
    ).group_by(UserModel.id)

    result = defaultdict(int)

    count_group = query.all()
    for visit in count_group:
        visit = dict(zip(['user_id', 'count'], visit))
        result[visit.get('user_id')] = visit.get('count')

    return result


def new_visit(info, email=None, url=None):
    user = get_or_create(db.session, UserModel, email=email)
    website = get_or_create(db.session, WebsiteModel, url=url)

    instance = VisitModel(user_id=user.id, website_id=website.id)
    db.session.add(instance)
    db.session.commit()

    return Visit.get_query(info).get(instance.id)
