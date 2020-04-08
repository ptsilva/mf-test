from application.services import users as users_service
from application.schema.users import User
import graphene
from typing import List


def resolve_user_by_id(_, info: graphene.ResolveInfo, id: int) -> User:
    return users_service.get_user_by_id(info=info, id=id)


def resolve_user_by_email(_, info: graphene.ResolveInfo, email: str) -> User:
    return users_service.get_user_by_email(info=info, email=email)


def resolve_users(_, info, limit: int = None, skip: int = None, sort_field: str = None, sort_order: str = None) -> List:
    return users_service.get_users(info, limit, skip, sort_field, sort_order)
