from datetime import datetime
from typing import List
from application.schema.stats import Stats
from application.services import stats as stats_service


def resolve_stats_total(_, info, initial_timestamp: datetime = None, final_timestamp: datetime = None) -> Stats:
    return stats_service.get_stats_total(info, initial_timestamp=initial_timestamp, final_timestamp=final_timestamp)


def resolve_stats_by_website(_, info, *args, **filters) -> List[Stats]:
    return stats_service.get_stats_by_website(info, filters)


def resolve_stats_by_user(_, info, *args, **filters) -> List[Stats]:
    return stats_service.get_stats_by_user(info, filters)
