from datetime import datetime, timedelta

db = None

def start_session(token: str, username: str) -> None:
	db.data.user_sessions.insert_one({
		'username': username,
		'token': token,
		'created': datetime.now(),
		'expires': datetime.now() + timedelta(days = 1)
	})

def valid_session(token: str) -> bool:
	session = db.data.user_sessions.find_one({'token': token})
	return True if session else False

def revoke_sessions(username: str) -> None:
	db.data.user_sessions.delete_many({'username': username})

def count_valid_sessions(username: str) -> int:
	return db.data.user_sessions.count({'username': username})
