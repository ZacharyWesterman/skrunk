"""application.db.weather"""

import application.exceptions as exceptions

from bson.objectid import ObjectId
from pymongo.database import Database
from datetime import datetime

## A pointer to the database object.
db: Database = None


def process_weather_user(userdata: dict) -> dict:
	"""
	Processes the weather-related user data.

	This function takes a dictionary containing user data, validates the user ID,
	retrieves additional user information from the database if necessary, and
	processes the 'max' and 'min' weather values.

	Args:
		userdata (dict): A dictionary containing user data. Expected keys are:
			- '_id': The user ID, which should be a valid ObjectId.
			- 'max': The maximum weather value (optional, should be a float).
			- 'min': The minimum weather value (optional, should be a float).

	Returns:
		dict: The processed user data dictionary with the following keys:
			- 'username': The username associated with the user ID, or the user ID itself if not found.
			- 'max': A dictionary with the following keys:
				- 'value': The maximum weather value (float).
				- 'default': A boolean indicating if the 'max' value was not provided.
				- 'disable': A boolean indicating if the 'max' value is explicitly set to False.
			- 'min': A dictionary with the following keys:
				- 'value': The minimum weather value (float).
				- 'default': A boolean indicating if the 'min' value was not provided.
				- 'disable': A boolean indicating if the 'min' value is explicitly set to False.
	"""
	if ObjectId.is_valid(userdata['_id']):
		db_user_data = db.users.find_one({'_id': userdata['_id']})
		userdata['username'] = userdata['_id'] if db_user_data is None else db_user_data['username']
	else:
		userdata['username'] = userdata['_id']

	userdata['max'] = {
		'value': userdata.get('max') if type(userdata.get('max')) is float else 0.0,
		'default': userdata.get('max') is None,
		'disable': userdata.get('max') == False,
	}
	userdata['min'] = {
		'value': userdata.get('min') if type(userdata.get('min')) is float else 0.0,
		'default': userdata.get('min') is None,
		'disable': userdata.get('min') == False,
	}

	return userdata


def get_users() -> list:
	"""
	Retrieve and process weather users from the database.

	This function fetches all weather users from the `db.weather_users` collection,
	processes each user using the `process_weather_user` function, and returns a
	sorted list of processed users. The sorting is based on the concatenation of
	the integer value of the 'exclude' field and the 'username' field.

	Returns:
		list: A sorted list of processed weather users.
	"""
	users = [process_weather_user(user) for user in db.weather_users.find({})]
	return sorted(users, key=lambda elem: str(int(elem['exclude'])) + elem['username'])


def get_weather_user(username: str) -> dict:
	"""
	Retrieve weather user data from the database based on the provided username.

	Args:
		username (str): The username of the user whose weather data is to be retrieved.

	Returns:
		dict: A dictionary containing the weather user data.

	Raises:
		UserDoesNotExistError: If the user with the given username does not exist in the database.
	"""
	db_user_data = db.users.find_one({'username': username})
	if db_user_data is None:
		raise exceptions.UserDoesNotExistError(username)

	userdata = db.weather_users.find_one({'_id': db_user_data['_id']})
	if userdata is None:
		raise exceptions.UserDoesNotExistError(username)

	return userdata


def create_user(user_data: dict) -> dict:
	"""
	Creates a new weather user in the database.

	This function first checks if the user exists in the main users collection.
	If the user does not exist, it raises a UserDoesNotExistError.
	If the user already exists in the weather_users collection, it raises a UserExistsError.

	The function then processes the 'max' and 'min' fields in the user_data to determine
	their values based on the 'disable' and 'default' flags.

	Finally, it inserts the new user data into the weather_users collection and returns
	the processed weather user data.

	Args:
		user_data (dict): A dictionary containing user information. Expected keys are:
			- 'username' (str): The username of the user.
			- 'lat' (float): The latitude of the user's location.
			- 'lon' (float): The longitude of the user's location.
			- 'max' (dict): A dictionary with 'disable' (bool) and 'default' (bool) keys.
			- 'min' (dict): A dictionary with 'disable' (bool) and 'default' (bool) keys.

	Returns:
		dict: The processed weather user data.

	Raises:
		UserDoesNotExistError: If the user does not exist in the main users collection.
		UserExistsError: If the user already exists in the weather_users collection.
	"""
	db_user_data = db.users.find_one({'username': user_data['username']})
	if db_user_data is None:
		raise exceptions.UserDoesNotExistError(user_data['username'])

	userdata = db.weather_users.find_one({'_id': db_user_data['_id']})
	if userdata:
		raise exceptions.UserExistsError(user_data['username'])

	user_max = False if user_data['max']['disable'] else (None if user_data['max']['default'] else user_data['max'])
	user_min = False if user_data['min']['disable'] else (None if user_data['min']['default'] else user_data['min'])

	userdata = {
		'_id': db_user_data['_id'],
		'lat': user_data['lat'],
		'lon': user_data['lon'],
		'max': user_max,
		'min': user_min,
		'last_sent': None,
		'exclude': False,
	}
	db.weather_users.insert_one(userdata)

	return process_weather_user(userdata)


def delete_user(username: str) -> dict:
	"""
	Delete a user from the weather database.

	Args:
		username (str): The username of the user to be deleted.

	Returns:
		dict: The user's previous (now nonexistent) weather information.
	"""
	userdata = get_weather_user(username)
	db.weather_users.delete_one({'_id': userdata['_id']})
	return process_weather_user(userdata)


def set_user_excluded(username: str, exclude: bool) -> dict:
	"""
	Updates the exclusion status of a weather user and processes the updated user data.

	Args:
		username (str): The username of the weather user.
		exclude (bool): The exclusion status to be set for the user.

	Returns:
		dict: The processed user data after updating the exclusion status.
	"""
	userdata = get_weather_user(username)
	db.weather_users.update_one({'_id': userdata['_id']}, {'$set': {'exclude': exclude}})
	userdata['exclude'] = exclude
	return process_weather_user(userdata)


def update_user(user_data: dict) -> dict:
	"""
	Updates the weather information for a user in the database.

	Args:
		user_data (dict): A dictionary containing user data with the following keys:
			- 'username' (str): The username of the user.
			- 'lat' (float): The latitude of the user's location.
			- 'lon' (float): The longitude of the user's location.
			- 'max' (dict): A dictionary with keys 'disable', 'default', and 'value' for the maximum temperature settings.
			- 'min' (dict): A dictionary with keys 'disable', 'default', and 'value' for the minimum temperature settings.
			- '_id' (Any): The unique identifier of the user in the database.

	Returns:
		dict: The user's updated weather information.
	"""
	weather_user = get_weather_user(user_data['username'])
	user_max = False if user_data['max']['disable'] else (None if user_data['max']['default'] else user_data['max']['value'])
	user_min = False if user_data['min']['disable'] else (None if user_data['min']['default'] else user_data['min']['value'])

	userdata = {
		'lat': user_data['lat'],
		'lon': user_data['lon'],
		'max': user_max,
		'min': user_min,
	}
	db.weather_users.update_one(
		{'_id': weather_user['_id']},
		{'$set': userdata}
	)

	return process_weather_user(get_weather_user(user_data['username']))


def get_last_exec() -> dict | None:
	"""
	Retrieves the most recent weather log entry from the database.

	Returns:
		dict | None: The most recent weather log entry as a dictionary if it exists, 
					 otherwise None.
	"""
	return db.weather_log.find_one({}, sort=[('timestamp', -1)])


def get_alert_history(username: str | None, start: int, count: int) -> list:
	"""
	Retrieve a list of alert history records from the database.

	Args:
		username (str | None): The username to filter the alert history by. If None, retrieves all alert history.
		start (int): The starting index for the records to retrieve.
		count (int): The number of records to retrieve.

	Returns:
		list: A list of dictionaries containing alert history records. Each dictionary contains:
			- 'recipient' (str): The recipient of the alert.
			- 'message' (str): The message content of the alert.
			- 'sent' (datetime): The timestamp when the alert was sent.
	"""
	selection = db.alert_history.find({} if username is None else {'to': username}, sort=[('_id', -1)])

	result = []
	for i in selection.limit(count).skip(start):
		result += [{
			'recipient': i['to'],
			'message': i['message'],
			'sent': i['_id'].generation_time,
		}]

	return result


def count_alert_history(username: str | None) -> list:
	"""
	Count the number of alert history documents in the database.

	Args:
		username (str | None): The username to filter the alert history by. If None, count all alert history documents.

	Returns:
		list: The count of alert history documents matching the criteria.
	"""
	return db.alert_history.count_documents({} if username is None else {'to': username})


def log_weather_alert(users: list[str], error: str | None) -> None:
	"""
	Logs a weather alert to the database.

	Args:
		users (list[str]): A list of user identifiers who are affected by the weather alert.
		error (str | None): An optional error message if there was an issue with the weather alert.

	Returns:
		None
	"""
	db.weather_log.insert_one({
		'timestamp': datetime.utcnow(),
		'users': users,
		'error': error,
	})


def log_user_weather_alert(username: str, message: str) -> None:
	"""
	Logs a weather alert message for a user.

	This function updates the last sent time for the user's weather alert
	and logs the alert message in the alert history.

	Args:
		username (str): The username of the user to log the alert for.
		message (str): The weather alert message to log.

	Returns:
		None
	"""
	db_user_data = db.users.find_one({'username': username})
	if db_user_data:
		now = datetime.utcnow()
		db.weather_users.update_one(
			{'_id': db_user_data['_id']},
			{'$set': {'last_sent': now}}
		)

	db.alert_history.insert_one({
		'to': username,
		'message': message,
	})
