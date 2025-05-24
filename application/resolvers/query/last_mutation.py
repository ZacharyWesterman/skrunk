"""application.resolvers.query.last_mutation"""

from graphql.type import GraphQLResolveInfo

from application.resolvers.mutation import mutation
from application.resolvers.query import query


@query.field('getLastMutation')
def resolve_get_last_mutation(_, info: GraphQLResolveInfo) -> dict | None:
	"""Get the last mutation called."""
	return mutation.get_last_mutation()
