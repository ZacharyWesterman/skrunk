"""application.resolvers.mutation.sessions"""

from graphql.type import GraphQLResolveInfo

import application.db.perms as perms
from application.db.sessions import count_valid_sessions, revoke_sessions

from . import mutation


@mutation.field('revokeSessions')
@perms.require('admin', perform_on_self=True)
def resolve_revoke_user_sessions(_, info: GraphQLResolveInfo, username: str) -> int:
	session_count = count_valid_sessions(username)
	revoke_sessions(username)
	return session_count
