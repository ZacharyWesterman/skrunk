from datetime import datetime, timedelta
from application.db.users import get_user_data

from pymongo.collection import Collection
db: Collection = None

def start_session(token: str, username: str) -> None:
	userdata = get_user_data(username)

	#Persistent logins last a very long time, but still get kicked eventually.
	expiry = datetime.now() + timedelta(weeks = 20) if 'persistent' in userdata['perms'] else datetime.now() + timedelta(days = 7)

	db.insert_one({
		'username': username,
		'token': token,
		'created': datetime.now(),
		'expires': expiry
	})

def valid_session(token: str) -> bool:
	session = db.find_one({'token': token})
	return True if session else False

def revoke_sessions(username: str) -> None:
	db.delete_many({'username': username})

def count_valid_sessions(username: str) -> int:
	return db.count_documents({'username': username})

def get_first_session_token(username: str) -> str | None:
	data = db.find_one({'username': username})

	if data is None:
		return None

	return data['token']
