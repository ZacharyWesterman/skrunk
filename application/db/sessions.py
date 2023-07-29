from datetime import datetime, timedelta
from application.db.users import get_user_data

db = None

def start_session(token: str, username: str) -> None:
	userdata = get_user_data(username)

	expiry = timedelta(years = 9001) if 'persistent' in userdata['perms'] else timedelta(days = 7)

	db.insert_one({
		'username': username,
		'token': token,
		'created': datetime.now(),
		'expires': datetime.now() + expiry
	})

def valid_session(token: str) -> bool:
	session = db.find_one({'token': token})
	return True if session else False

def revoke_sessions(username: str) -> None:
	db.delete_many({'username': username})

def count_valid_sessions(username: str) -> int:
	return db.count_documents({'username': username})
