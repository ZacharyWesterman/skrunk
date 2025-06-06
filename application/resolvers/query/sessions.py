"""application.resolvers.query.sessions"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.sessions import count_valid_sessions

from . import query


@query.field('countSessions')
@perms.require('admin', perform_on_self=True)
def resolve_count_user_sessions(_, _info: GraphQLResolveInfo, username: str) -> int:
	return count_valid_sessions(username)
