"""application.db.apikeys"""

import random
import string
from datetime import datetime
from pymongo.collection import Collection

from . import perms


## A pointer to the API keys collection in the database.
db: Collection = None  # type: ignore[assignment]


def valid_api_key(key: str) -> bool:
	"""
	Checks if the provided API key is valid by searching for it in the database.

	Args:
		key (str): The API key to be validated.

	Returns:
		bool: True if the API key is found in the database, False otherwise.
	"""
	return True if db.find_one({'key': key}) else False


def new_api_key(description: str, permissions: list[str]) -> str:
	"""
	Generate a new API key with the given description and permissions.

	Args:
		description (str): A description for the new API key.
		permissions (list[str]): A list of permissions associated with the API key.

	Returns:
		str: The generated API key.
	"""
	# Generate random 30-digit API key. This probably will not clash with an existing key.
	api_key = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))

	user_data = perms.caller_info_strict()

	db.insert_one({
		'key': api_key,
		'description': description,
		'creator': user_data['_id'],
		'created': datetime.utcnow(),
		'perms': permissions,
	})

	return api_key


def delete_api_key(key: str) -> bool:
	"""
	Deletes an API key from the database.

	Args:
		key (str): The API key to be deleted.

	Returns:
		bool: True if the API key was successfully deleted, False otherwise.
	"""
	return True if db.delete_one({'key': key}).deleted_count else False


def get_api_keys() -> list:
	"""
	Retrieve a list of API keys from the database.

	This function queries the database to find API keys, sorts them by the 
	'created' field in descending order, and limits the result to 200 entries.

	Returns:
		list: A list of API keys sorted by creation date in descending order.
	"""
	# Should never have this many API keys floating around, but just in case.
	return [i for i in db.find(sort=[('created', -1)]).limit(200)]
