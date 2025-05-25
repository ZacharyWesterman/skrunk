"""application.resolvers.query.apikeys"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.apikeys import get_api_keys

from . import query


@query.field('getAPIKeys')
@perms.require('admin')
def resolve_get_api_keys(_, _info: GraphQLResolveInfo) -> list:
	"""
	Resolver function to get API keys.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: A list of API keys.
	"""
	return get_api_keys()
