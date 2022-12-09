from application.db.sessions import revoke_sessions, count_valid_sessions
import application.db.creds as creds

@creds.require(['admin'])
def resolve_revoke_user_sessions(_, info, username: str) -> int:
	session_count = count_valid_sessions(username)
	revoke_sessions(username)
	return session_count
