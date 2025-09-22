"""application.db.users"""

import shutil
import uuid
from datetime import datetime, timedelta
from typing import TypeVar
from zipfile import ZipFile

import bcrypt
from bson import json_util
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from ..types import BlobSearchFilter, InventorySearchFilter, UserData

FILTER = TypeVar('FILTER', BlobSearchFilter, InventorySearchFilter)

## A pointer to the users collection in the database.
db: Collection = None  # type: ignore[assignment]

## A pointer to the main database.
top_level_db: Database = None  # type: ignore[assignment]


def is_locked(failed_logins: int) -> bool:
	"""
	Checks if a user is locked based on the number of failed login attempts.

	Args:
		failed_logins (int): The number of failed login attempts.

	Returns:
		bool: True if the user is locked, False otherwise.
	"""
	return failed_logins >= 5


def login_attempts_remaining(failed_logins: int) -> int:
	"""
	Calculates the number of login attempts remaining before the user is locked.

	Args:
		failed_logins (int): The number of failed login attempts.

	Returns:
		int: The number of login attempts remaining.
	"""
	return max(0, 5 - failed_logins)


def process_user_data(userdata: dict) -> UserData:
	"""
	Process user data to ensure it has the correct structure.

	Args:
		userdata (dict): The user data to process.

	Returns:
		UserData: The processed user data.
	"""
	userdata['is_locked'] = is_locked(userdata.get('failed_logins', 0))
	userdata['disabled_modules'] = settings.calculate_disabled_modules(
		userdata.get('disabled_modules', [])
	)

	return UserData(**userdata)


def get_admins() -> list:
	"""
	Returns:
		list: A list of all admin users.
	"""
	return list(db.find({'perms': 'admin'}))


def count_users() -> int:
	"""
	Returns:
		int: The count of all non-ephemeral users.
	"""
	return db.count_documents({'ephemeral': {'$not': {'$eq': True}}})


def get_user_list(groups: list[str]) -> list:
	"""
	Returns a list of users with their username, display name, and last login.

	Args:
		groups (list, optional): List of groups to filter users by. Defaults to [].

	Returns:
		list: A list of users.
	"""
	query = {'$or': [{'groups': i} for i in groups]} if len(groups) else {}
	return [{
		'username': data['username'],
		'display_name': data['display_name'],
		'last_login': data.get('last_login'),
	} for data in db.find(query, sort=[('username', 1)])]


def userids_in_groups(groups: list) -> list[ObjectId]:
	"""
	Returns a list of user IDs for users in the specified groups.

	Args:
		groups (list): List of groups to filter users by.

	Returns:
		list: A list of user IDs.
	"""
	query = {'$or': [{'groups': i} for i in groups]} if len(groups) else {}
	result = []
	for i in db.find(query):
		result += [i['_id']]
	return result


def get_user_by_id(id: ObjectId) -> UserData:
	"""
	Returns user data for the user with the specified ID.

	Args:
		id (ObjectId): The ID of the user.

	Returns:
		UserData: The user data.

	Raises:
		UserDoesNotExistError: If the user is not found.
	"""
	userdata = db.find_one({'_id': id})
	if userdata is None:
		raise exceptions.UserDoesNotExistError(f'ID:{id}')

	return process_user_data(userdata)


def get_user_data(username: str) -> UserData:
	"""
	Returns user data for the user with the specified username.

	Args:
		username (str): The username of the user.

	Returns:
		dict: The user data.

	Raises:
		UserDoesNotExistError: If the user is not found.
	"""
	userdata = db.find_one({'username': username})

	if userdata is None:
		raise exceptions.UserDoesNotExistError(username)

	return process_user_data(userdata)


def update_user_theme(username: str, theme: dict) -> dict:
	"""
	Updates the theme for the user with the specified username.

	Args:
		username (str): The username of the user.
		theme (dict): The new theme data.

	Returns:
		dict: The updated user data.

	Raises:
		UserDoesNotExistError: If the user is not found.
	"""
	userdata = db.find_one({'username': username})

	if userdata is None:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'theme': theme}})

	userdata['theme'] = theme
	return userdata


def update_user_perms(username: str, perms: list) -> dict:
	"""
	Updates the permissions for the user with the specified username.

	Args:
		username (str): The username of the user.
		perms (list): The new permissions.

	Returns:
		dict: The updated user data.

	Raises:
		UserDoesNotExistError: If the user is not found.
	"""
	userdata = db.find_one({'username': username})

	if userdata is None:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'perms': perms}})

	userdata['perms'] = perms
	return userdata


def create_user(
    username: str,
    password: str,
    *,
    groups: list,
    admin: bool = False,
    ephemeral: bool = False
) -> dict:
	"""
	Creates a new user with the specified username, password,
	groups, admin status, and ephemeral status.

	Args:
		username (str): The username of the new user.
		password (str): The password of the new user.
		groups (list, optional): List of groups the user belongs to. Defaults to [].
		admin (bool, optional): Whether the user is an admin. Defaults to False.
		ephemeral (bool, optional): Whether the user is ephemeral. Defaults to False.

	Returns:
		dict: The created user data.

	Raises:
		BadUserNameError: If the username is empty.
		UserExistsError: If the user already exists.
	"""
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
		'failed_logins': 0,
	}

	db.insert_one(userdata)
	settings.update_groups([], groups)

	return userdata


def delete_user(username: str) -> dict:
	"""
	Deletes the user with the specified username.

	Args:
		username (str): The username of the user to delete.

	Returns:
		dict: The deleted user data.

	Raises:
		UserDoesNotExistError: If the user is not found.
	"""
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.delete_one({'username': username})
	return userdata


def update_user_password(username: str, password: str) -> dict:
	"""
	Updates the password for the user with the specified username.

	Args:
		username (str): The username of the user.
		password (str): The new password.

	Returns:
		dict: The updated user data.

	Raises:
		BadUserNameError: If the username is empty.
		UserDoesNotExistError: If the user is not found.
	"""
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
	"""
	Updates the username for the user with the specified username.

	Args:
		username (str): The current username of the user.
		new_username (str): The new username.

	Returns:
		dict: The updated user data.

	Raises:
		BadUserNameError: If the new username is empty.
		UserDoesNotExistError: If the user is not found.
		UserExistsError: If the new username already exists.
	"""
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
	"""
	Updates the display name for the user with the specified username.

	Args:
		username (str): The username of the user.
		display_name (str): The new display name.

	Returns:
		dict: The updated user data.

	Raises:
		BadUserNameError: If the username is empty.
		UserDoesNotExistError: If the user is not found.
	"""
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
	"""
	Updates the email for the user with the specified username.

	Args:
		username (str): The username of the user.
		email (str): The new email.

	Returns:
		dict: The updated user data.

	Raises:
		BadUserNameError: If the username is empty.
		UserDoesNotExistError: If the user is not found.
	"""
	if len(username) == 0:
		raise exceptions.BadUserNameError

	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'email': email}})

	userdata['email'] = email
	return userdata


def update_user_groups(username: str, groups: list) -> dict:
	"""
	Updates the groups for the user with the specified username.

	Args:
		username (str): The username of the user.
		groups (list): The new groups.

	Returns:
		dict: The updated user data.

	Raises:
		BadUserNameError: If the username is empty.
		UserDoesNotExistError: If the user is not found.
	"""
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
	"""
	Updates the disabled modules for the user with the specified username.

	Args:
		username (str): The username of the user.
		module (str): The module to update.
		disabled (bool): Whether the module is disabled.

	Returns:
		dict: The updated user data.

	Raises:
		BadUserNameError: If the username is empty.
		UserDoesNotExistError: If the user is not found.
	"""
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
	"""
	Authenticates the user with the specified username and password.

	Args:
		username (str): The username of the user.
		password (str): The password of the user.

	Returns:
		str: A login token if authentication is successful.

	Raises:
		UserDoesNotExistError: If the user does not exist.
		UserIsLocked: If the user is locked due to too many failed login attempts.
		AuthenticationError: If authentication fails.
	"""
	userdata = db.find_one({'username': username})

	if userdata is None:
		raise exceptions.UserDoesNotExistError(username)

	if is_locked(userdata.get('failed_logins', 0)):
		raise exceptions.UserIsLocked

	# If the password is not correct, increment the failed logins and raise an error
	if not bcrypt.checkpw(password.encode(), userdata['password']):
		db.update_one({'_id': userdata['_id']}, {'$inc': {'failed_logins': 1}})
		raise exceptions.AuthenticationError(login_attempts_remaining(userdata.get('failed_logins', 0)))

	login_token = tokens.create_user_token(username)
	db.update_one({'_id': userdata['_id']}, {'$set': {
		'last_login': datetime.utcnow(),
		'failed_logins': 0,  # Reset failed logins on successful authentication
	}})

	return login_token


def group_filter(
	filter: FILTER,
	user_data: dict
) -> FILTER:
	"""
	Applies group filtering to the specified filter based on the user's groups.

	Args:
		filter (Filter): The filter to apply group filtering to.
		user_data (dict): The user data containing the groups.

	Returns:
		dict: The updated filter.
	"""
	if filter.get('creator') is None:
		groups = user_data.get('groups', [])
		if len(groups):
			filter['creator'] = userids_in_groups(groups)  # type: ignore[assignment]

	return filter


def dump_collection(collection: str, queries: list, fp: ZipFile) -> None:
	"""
	Exports documents from a specified MongoDB collection based on provided queries
	and writes them to a ZipFile as JSON.
	Any sensitive information, such as passwords, is excluded from the export.

	Args:
		collection (str): The name of the MongoDB collection to export.
		queries (list): A list of query dictionaries to filter documents for export.
		fp (ZipFile): An open ZipFile object to which the exported JSON will be written.
	"""

	items = []

	# Get a list of documents to export
	this_coll = top_level_db[collection]
	for i in queries:
		if this_coll.count_documents(i) > 0:
			def doc_mutate(data: dict) -> dict:
				return data

			if collection == 'feeds':
				def m2(data: dict) -> dict:
					data['documents'] = [i for i in top_level_db.documents.find({'feed': data['_id']})]
					return data
				doc_mutate = m2
			elif collection == 'users':
				def m2(data: dict) -> dict:
					del data['password']
					return data
				doc_mutate = m2

			items = [doc_mutate(i) for i in this_coll.find(i)]

	# Don't add to export if there are no documents
	if len(items) == 0:
		return

	fp.writestr(f'{collection}.json', json_util.dumps(items, indent=2))


def export_user_data(username: str) -> dict:
	"""
	Exports the user data for the user with the specified username.

	Args:
		username (str): The username of the user.

	Returns:
		dict: A blob containing the exported data.

	Raises:
		UserDoesNotExistError: If the user is not found.
	"""
	# Returns a blob after creating a ZIP file containing user data.

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

	# Create a ZIP file and blob entry
	blob_storage = blob.BlobStorage(*blob.create_blob(
		'data_export.zip',
		tags=['export', '__temp_file'],
		hidden=False,
		ephemeral=True
	))
	temp_filename = f'/tmp/{uuid.uuid4()}.zip'
	with ZipFile(temp_filename, 'w') as fp:
		# Iterate over all collections, and append the file to the ZIP file.
		iter = (i for i in top_level_db.list_collection_names() if i not in exclude_collections)
		for collection in iter:
			dump_collection(collection, queries, fp)

	# Move the ZIP file to the blob storage path
	print('Moving ZIP file to blob storage...', flush=True)
	shutil.move(temp_filename, blob_storage.path(create=True))

	size, md5sum = blob.file_info(blob_storage.path())
	blob.mark_as_completed(blob_storage.id, size, md5sum)

	print(f'Finished exporting {username}\'s data.', flush=True)

	return blob.get_blob_data(blob_storage.id)


def unlock_user(username: str) -> UserData:
	"""
	Unlocks the user with the specified username by resetting their failed login attempts.

	Args:
		username (str): The username of the user to unlock.

	Returns:
		UserData: The updated user data.

	Raises:
		UserDoesNotExistError: If the user is not found.
	"""
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	db.update_one({'username': username}, {'$set': {'failed_logins': 0}})

	return process_user_data(userdata)


def create_reset_code(username: str) -> str:
	"""
	Create a password reset code for the user with the specified username.

	Args:
		username (str): The username of the user requesting the reset code.

	Returns:
		str: The generated reset code.

	Raises:
		UserDoesNotExistError: If the user is not found.
		RateLimitExceeded: If the user has exceeded the rate limit for requesting reset codes.
	"""
	userdata = db.find_one({'username': username})

	if not userdata:
		raise exceptions.UserDoesNotExistError(username)

	# Rate limit: Only allow 3 reset codes in the last 10 minutes.
	# Hopefully this is sufficient to prevent abuse.
	recent_requests = top_level_db.reset_codes.count_documents({
		'username': username,
		'created': {'$gte': datetime.utcnow() - timedelta(minutes=10)}
	})

	if recent_requests >= 3:
		raise exceptions.RateLimitExceeded()

	# Create 6-digit code and store it in the database
	code = ''.join(str(uuid.uuid4())[0:6]).lower()
	top_level_db.reset_codes.insert_one({
		'username': username,
		'code': code,
		'created': datetime.utcnow(),
	})

	return code


# These imports are needed at this location to avoid circular imports
# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position

from application import exceptions, tokens  # nopep8
from application.db import blob, settings  # nopep8

# pylint: enable=wrong-import-position
# pylint: enable=wrong-import-order
