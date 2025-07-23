"""application.resolvers.query.sessions"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.sessions import count_valid_sessions

from . import query


@query.field('countSessions')
@perms.require('admin', perform_on_self=True)
def resolve_count_user_sessions(_, _info: GraphQLResolveInfo, username: str) -> int:
	"""
	Resolves the total number of valid sessions for a given user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for which to count valid sessions.

	Returns:
		int: The number of valid sessions associated with the specified username.
	"""
	return count_valid_sessions(username)
