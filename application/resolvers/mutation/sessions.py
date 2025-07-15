"""application.resolvers.mutation.sessions"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.sessions import count_valid_sessions, revoke_sessions

from . import mutation


@mutation.field('revokeSessions')
@perms.require('admin', perform_on_self=True)
def resolve_revoke_user_sessions(_, _info: GraphQLResolveInfo, username: str) -> int:
	"""
	Revokes all active sessions for a given user and returns the number of sessions that were revoked.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username whose sessions are to be revoked.

	Returns:
		int: The number of sessions that were revoked for the specified user.
	"""
	session_count = count_valid_sessions(username)
	revoke_sessions(username)
	return session_count
