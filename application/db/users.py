import application.exceptions as exceptions
from pymongo import MongoClient

import bcrypt

__mongo_url = 'mongodb://192.168.1.184:27017/'
db = MongoClient(__mongo_url)

def get_user_list() -> list:
	global db
	return [ data['username'] for data in db.data.users.find({}) ]

def get_user_data(username: str) -> dict:
	global db
	userdata = db.data.users.find_one({'username': username})

	if userdata:
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(username)

def update_user_theme(username: str, theme: list) -> dict:
	global db
	userdata = db.data.users.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.data.users.update_one({'username': username}, {'$set': {'theme': theme}})

	userdata['theme'] = theme
	return userdata

def create_user(username: str, password: str) -> dict:
	global db

	if len(username) == 0:
		raise exceptions.InvalidUsername

	userdata = db.data.users.find_one({'username': username})

	if userdata:
		raise exceptions.UserExistsError(username)

	db.data.users.insert_one({
		'username': username,
		'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
		'theme': [],
		'creds': [],
	})

	return {'username': username, 'theme': []}

def delete_user(username: str) -> None:
	global db
	userdata = db.data.users.find_one({'username': username})

	if userdata:
		db.data.users.delete_one({'username': username})
	else:
		raise exceptions.UserDoesNotExistError(username)

def authenticate(username: str, password: str) -> str:
	userdata = get_user_data(username)

	if not bcrypt.checkpw(password.encode(), userdata.get('password')):
		raise exceptions.AuthenticationError

	login_token = create_user_token(username)

	return login_token

from application.tokens import create_user_token
