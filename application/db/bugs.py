from application.tokens import decode_user_token, get_request_token
from . import users

from bson.objectid import ObjectId
from datetime import datetime

db = None

def report_bug(text: str) -> bool:
	try:
		username = decode_user_token(get_request_token()).get('username')
		user_data = users.get_user_data(username)
	except exceptions.UserDoesNotExistError:
		return False

	db.insert_one({
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'body': text,
		'convo': [],
		'resolved': False,
	})

	return True
