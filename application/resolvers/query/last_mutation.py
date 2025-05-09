"""application.resolvers.query.last_mutation"""
from ariadne.types import GraphQLResolveInfo
from application.resolvers.query import query
from application.resolvers.mutation import mutation


@query.field('getLastMutation')
def resolve_get_last_mutation(_, info: GraphQLResolveInfo) -> dict | None:
	"""Get the last mutation called."""
	return mutation.get_last_mutation()
