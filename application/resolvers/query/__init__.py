from ariadne import QueryType
from .users import resolve_get_user, resolve_authenticate

query = QueryType()

query.set_field('getUser', resolve_get_user)
query.set_field('authenticate', resolve_authenticate)
