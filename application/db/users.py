import application.exceptions as exceptions
from datetime import datetime
import bcrypt
from bson.objectid import ObjectId

db = None

def get_user_list() -> list:
	global db
	return [ data['username'] for data in db.find({}) ]

def get_user_by_id(id: ObjectId) -> dict:
	global db
	userdata = db.find_one({'_id': id})
	if userdata:
		return userdata

	raise exceptions.UserDoesNotExistError(f'ID:{id}')

def get_user_data(username: str) -> dict:
	global db
	userdata = db.find_one({'username': username})

	if userdata:
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(username)

def update_user_theme(username: str, theme: list) -> dict:
	global db
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'theme': theme}})

	userdata['theme'] = theme
	return userdata

def update_user_perms(username: str, perms: list) -> dict:
	global db
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'perms': perms}})

	userdata['perms'] = perms
	return userdata

def create_user(username: str, password: str) -> dict:
	global db

	if len(username) == 0:
		raise exceptions.InvalidUsername

	userdata = db.find_one({'username': username})

	if userdata:
		raise exceptions.UserExistsError(username)

	userdata = {
		'username': username,
		'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
		'created': datetime.now(),
		'theme': [],
		'perms': [],
	}

	db.insert_one(userdata)
	return userdata

def delete_user(username: str) -> None:
	global db
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.delete_one({'username': username})
	return userdata

def update_user_password(username: str, password: str) -> dict:
	global db

	if len(username) == 0:
		raise exceptions.InvalidUsername

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {
		'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
	}})

	return userdata

def authenticate(username: str, password: str) -> str:
	userdata = get_user_data(username)

	if not bcrypt.checkpw(password.encode(), userdata.get('password')):
		raise exceptions.AuthenticationError

	login_token = create_user_token(username)

	return login_token

from application.tokens import create_user_token
