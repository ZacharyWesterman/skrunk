"""application.resolvers.query.last_mutation"""

from graphql.type import GraphQLResolveInfo

from application.resolvers.mutation import mutation
from application.resolvers.query import query


@query.field('getLastMutation')
def resolve_get_last_mutation(_, _info: GraphQLResolveInfo) -> dict | None:
	"""
	Retrieves information about the most recently called mutation.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict | None: A dictionary containing details of the last mutation if available, otherwise None.
	"""
	return mutation.get_last_mutation()
