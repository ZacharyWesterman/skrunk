from datetime import datetime
from zipfile import ZipFile, Path
from bson.objectid import ObjectId
from bson import json_util
import bcrypt

import application.exceptions as exceptions
from application.db import settings

from pymongo.collection import Collection
from pymongo.database import Database
db: Collection = None
top_level_db: Database = None

def get_admins() -> list:
	return [i for i in db.find({'perms': 'admin'})]

def count_users() -> int:
	return db.count_documents({'ephemeral': {'$not': {'$eq': True}}})

def get_user_list(groups: list = []) -> list:
	query = {'$or': [{'groups': i} for i in groups]} if len(groups) else {}
	return [ {
		'username': data['username'],
		'display_name': data['display_name'],
		'last_login': data.get('last_login'),
	} for data in db.find(query, sort=[('username', 1)]) ]

def userids_in_groups(groups: list) -> list:
	query = {'$or': [{'groups': i} for i in groups]} if len(groups) else {}
	result = []
	for i in db.find(query):
		result += [i['_id']]
	return result

def get_user_by_id(id: ObjectId) -> dict:
	userdata = db.find_one({'_id': id})
	if userdata:
		userdata['disabled_modules'] = settings.calculate_disabled_modules(userdata.get('disabled_modules', []))
		return userdata

	raise exceptions.UserDoesNotExistError(f'ID:{id}')

def get_user_data(username: str) -> dict:
	userdata = db.find_one({'username': username})

	if userdata:
		userdata['disabled_modules'] = settings.calculate_disabled_modules(userdata.get('disabled_modules', []))
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(username)

def update_user_theme(username: str, theme: dict) -> dict:
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'theme': theme}})

	userdata['theme'] = theme
	return userdata

def update_user_perms(username: str, perms: list) -> dict:
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'perms': perms}})

	userdata['perms'] = perms
	return userdata

def create_user(username: str, password: str, *, groups: list = [], admin: bool = False, ephemeral: bool = False) -> dict:
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
		'disabled_modules': [],
		'email': '',
	}

	db.insert_one(userdata)
	settings.update_groups([], groups)

	return userdata

def delete_user(username: str) -> None:
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.delete_one({'username': username})
	return userdata

def update_user_password(username: str, password: str) -> dict:
	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {
		'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
	}})

	return userdata

def update_username(username: str, new_username: str) -> dict:
	if len(new_username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})
	if not userdata:
		raise exceptions.UserDoesNotExistError(username)
	
	if db.find_one({'username': new_username}):
		raise exceptions.UserExistsError(new_username)

	db.update_one({'_id': userdata['_id']}, {'$set': {
		'username': new_username,
	}})
	userdata['username'] = new_username

	return userdata

def update_user_display_name(username: str, display_name: str) -> dict:

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

def update_user_email(username: str, email: str) -> dict:

	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'email': email}})

	userdata['email'] = email
	return userdata

def update_user_groups(username: str, groups: list) -> dict:
	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'groups': groups}})
	settings.update_groups(userdata.get('groups', []), groups)

	userdata['groups'] = groups
	return userdata

def update_user_module(username: str, module: str, disabled: bool) -> dict:
	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	modules: list[str] = userdata.get('disabled_modules', [])

	if disabled:
		modules += [module]
	elif module in modules:
		modules.remove(module)

	userdata['modules'] = list(set(modules))

	db.update_one({'_id': userdata['_id']}, {'$set': {
		'disabled_modules': userdata['modules'],
	}})

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

def export_user_data(username: str) -> dict:
	#Returns a blob after creating a ZIP file containing user data.

	print(f'Creating ZIP export of {username}\'s data...', flush=True)

	userdata = db.find_one({'username': username})
	if not userdata:
		raise exceptions.UserDoesNotExistError(username)
	
	user_id = userdata['_id']

	queries = [
		{'_id': user_id},
		{'_id': username},
		{'owner': user_id},
		{'creator': user_id},
	]

	exclude_collections = [
		'api_keys', 'subscriptions',
	]

	#Create a ZIP file and blob entry
	blob_storage = blob.BlobStorage(*blob.create_blob('data_export.zip', tags = ['export', '__temp_file'], hidden = False, ephemeral = True), '')
	fp = ZipFile(blob_storage.path(create = True), 'w')

	#Iterate over all collections, and append the file to the ZIP file.
	for collection in [i for i in top_level_db.list_collection_names() if i not in exclude_collections]:
		items = []

		#Get a list of documents to export
		this_coll = top_level_db[collection]
		for i in queries:
			if this_coll.count_documents(i) > 0:
				def doc_mutate(data: dict) -> dict:
					return data

				if collection == 'feeds':
					def doc_mutate(data: dict) -> dict:
						data['documents'] = [i for i in top_level_db.documents.find({'feed': data['_id']})]
						return data
				elif collection == 'users':
					def doc_mutate(data: dict) -> dict:
						del data['password']
						return data
				
				items = [doc_mutate(i) for i in this_coll.find(i)]

		#Don't add to export if there are no documents
		if len(items) == 0:
			continue

		fp.writestr(f'{collection}.json', json_util.dumps(items, indent=2))

	size, md5sum = blob.file_info(blob_storage.path())
	blob.mark_as_completed(blob_storage.id, size, md5sum)

	print(f'Finished exporting {username}\'s data.', flush=True)

	return blob.get_blob_data(blob_storage.id)

from application.tokens import create_user_token
from application.db import blob
