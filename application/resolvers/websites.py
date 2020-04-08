from application.services import websites as websites_service
from application.schema.websites import Website
from typing import List
import graphene


def resolve_website_by_id(_, info: graphene.ResolveInfo, id: int) -> Website:
    return websites_service.get_website_by_id(info=info, id=id)


def resolve_website_by_url(_, info: graphene.ResolveInfo, url: str) -> Website:
    return websites_service.get_website_by_url(info=info, url=url)


def resolve_websites(_, info, limit: int = None, skip: int = None, sort_field: str = None, sort_order: str = None) -> List:
    return websites_service.get_websites(info, limit, skip, sort_field, sort_order)

