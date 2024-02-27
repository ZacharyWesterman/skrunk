import application.exceptions as exceptions
from datetime import datetime
import bcrypt
from bson.objectid import ObjectId
import application.db.settings as settings

db = None

def get_admins() -> list:
	global db
	return [i for i in db.find({'perms': 'admin'})]

def count_users() -> int:
	global db
	return db.count_documents({'ephemeral': {'$not': {'$eq': True}}})

def get_user_list(groups: list = []) -> list:
	query = {'$or': [{'groups': i} for i in groups]} if len(groups) else {}
	return [ {'username': data['username'], 'display_name': data['display_name']} for data in db.find(query, sort=[('username', 1)]) ]

def userids_in_groups(groups: list) -> list:
	query = {'$or': [{'groups': i} for i in groups]} if len(groups) else {}
	result = []
	for i in db.find(query):
		result += [i['_id']]
	return result

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

def update_user_theme(username: str, theme: dict) -> dict:
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

def create_user(username: str, password: str, *, groups: list = [], admin: bool = False, ephemeral: bool = False) -> dict:
	global db

	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if userdata:
		raise exceptions.UserExistsError(username)

	userdata = {
		'username': username,
		'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
		'created': datetime.now(),
		'theme': {
			'colors': [],
			'sizes': [],
		},
		'perms': ['admin'] if admin else [],
		'display_name': username.title(),
		'ephemeral': ephemeral,
		'groups': groups,
	}

	db.insert_one(userdata)
	settings.add_groups(groups)

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
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {
		'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
	}})

	return userdata

def update_user_display_name(username: str, display_name: str) -> dict:
	global db

	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	if display_name == '':
		display_name = username.title()

	db.update_one({'username': username}, {'$set': {'display_name': display_name}})

	userdata['display_name'] = display_name
	return userdata

def update_user_groups(username: str, groups: list) -> dict:
	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'groups': groups}})
	settings.add_groups(groups)

	userdata['groups'] = groups
	return userdata

def authenticate(username: str, password: str) -> str:
	userdata = get_user_data(username)

	if not bcrypt.checkpw(password.encode(), userdata.get('password')):
		raise exceptions.AuthenticationError

	login_token = create_user_token(username)
	db.update_one({'_id': userdata['_id']}, {'$set':{'last_login': datetime.utcnow()}})

	return login_token

def group_filter(filter: dict, user_data: dict) -> dict:
	if filter.get('creator') is None:
		groups = user_data.get('groups', [])
		if len(groups):
			filter['creator'] = userids_in_groups(groups)

	return filter

from application.tokens import create_user_token
