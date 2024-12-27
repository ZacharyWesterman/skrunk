from datetime import datetime, timedelta
from application.db.users import get_user_data

from pymongo.collection import Collection
db: Collection = None


def start_session(token: str, username: str) -> None:
	"""
	Starts a new session for the given user.

	This function retrieves user data for the specified username and creates a new session
	in the database with the provided token. The session expiry time is determined based
	on the user's permissions. Persistent logins last for 20 weeks, while non-persistent
	logins last for 7 days.

	Args:
		token (str): The session token.
		username (str): The username of the user starting the session.

	Returns:
		None
	"""
	userdata = get_user_data(username)

	# Persistent logins last a very long time, but still get kicked eventually.
	expiry = datetime.now() + timedelta(weeks=20) if 'persistent' in userdata['perms'] else datetime.now() + timedelta(days=7)

	db.insert_one({
		'username': username,
		'token': token,
		'created': datetime.now(),
		'expires': expiry
	})


def valid_session(token: str) -> bool:
	"""
	Check if a session with the given token exists in the database.

	Args:
		token (str): The session token to validate.

	Returns:
		bool: True if a session with the token exists, False otherwise.
	"""
	session = db.find_one({'token': token})
	return True if session else False


def revoke_sessions(username: str) -> None:
	"""
	Revoke all sessions for a given username.

	This function deletes all session records associated with the specified username
	from the database.

	Args:
		username (str): The username whose sessions are to be revoked.

	Returns:
		None
	"""
	db.delete_many({'username': username})


def count_valid_sessions(username: str) -> int:
	"""
	Count the number of valid sessions for a given username.

	Args:
		username (str): The username to count sessions for.

	Returns:
		int: The number of valid sessions associated with the username.
	"""
	return db.count_documents({'username': username})


def get_first_session_token(username: str) -> str | None:
	"""
	Retrieve the first session token for a given username.

	Args:
		username (str): The username to search for in the database.

	Returns:
		str | None: The session token if found, otherwise None.
	"""
	data = db.find_one({'username': username})

	if data is None:
		return None

	return data['token']
