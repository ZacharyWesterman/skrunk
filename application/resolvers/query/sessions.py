from application.db.sessions import revoke_sessions, count_valid_sessions
import application.db.perms as perms
from . import query


@query.field('countSessions')
@perms.require('admin', perform_on_self=True)
def resolve_count_user_sessions(_, info, username: str) -> int:
	return count_valid_sessions(username)
