from application.models import VisitModel, UserModel, WebsiteModel
from application import schema
from sqlalchemy import and_, desc, asc, func, extract


def apply_filters(query, filters: dict):
    """
    Common way to apply shared filters across tables
    """

    if filters.get('initial_timestamp'):
        query = query.filter(VisitModel.timestamp >= filters.get('initial_timestamp'))

    if filters.get('final_timestamp'):
        query = query.filter(VisitModel.timestamp <= filters.get('final_timestamp'))

    if filters.get('min_age') is not None:
        query = query.filter(extract('year', func.age(UserModel.date_of_birth)) >= filters.get('min_age'))

    if filters.get('max_age') is not None:
        query = query.filter(extract('year', func.age(UserModel.date_of_birth)) <= filters.get('max_age'))

    if filters.get('gender'):
        query = query.filter(UserModel.gender == filters.get('gender'))

    if filters.get('users'):
        query = query.filter(UserModel.email.in_(filters.get('users')))

    if filters.get('websites'):
        query = query.filter(WebsiteModel.url.in_(filters.get('websites')))
    return query


def get_or_create(session, model, **kwargs):
    """Perform fetch or create model on database"""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def model2dict(model):
    d = {}
    for column in model.__table__.columns:
        d[column.name] = str(getattr(model, column.name))

    return d
