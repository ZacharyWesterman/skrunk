from ariadne import QueryType
from .users import resolve_get_user

query = QueryType()

query.set_field('getUser', resolve_get_user)
