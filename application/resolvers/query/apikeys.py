"""application.resolvers.query.apikeys"""

from ariadne.types import GraphQLResolveInfo
from application.db.apikeys import get_api_keys
from application.db import perms
from . import query


@query.field('getAPIKeys')
@perms.require('admin')
def resolve_get_api_keys(_, info: GraphQLResolveInfo) -> list:
	"""
	Resolver function to get API keys.

	Args:
		_ (Any): Placeholder.
		info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: A list of API keys.
	"""
	return get_api_keys()
