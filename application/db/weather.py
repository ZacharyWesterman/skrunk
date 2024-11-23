import application.exceptions as exceptions

from bson.objectid import ObjectId
from pymongo.database import Database
from datetime import datetime

db: Database = None

def process_weather_user(userdata: dict) -> dict:
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
	users = [ process_weather_user(user) for user in db.weather_users.find({}) ]
	return sorted(users, key = lambda elem: str(int(elem['exclude']))+elem['username'])

def get_weather_user(username: str) -> dict:
	db_user_data = db.users.find_one({'username': username})
	if db_user_data is None:
		raise exceptions.UserDoesNotExistError(username)
	
	userdata = db.weather_users.find_one({'_id': db_user_data['_id']})
	if userdata is None:
		raise exceptions.UserDoesNotExistError(username)
	
	return userdata

def create_user(user_data: dict) -> dict:
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

def delete_user(username: str) -> None:
	userdata = get_weather_user(username)
	db.weather_users.delete_one({'_id': userdata['_id']})
	return process_weather_user(userdata)

def set_user_excluded(username: str, exclude: bool) -> dict:
	userdata = get_weather_user(username)
	db.weather_users.update_one({'_id': userdata['_id']}, {'$set': {'exclude': exclude}})
	userdata['exclude'] = exclude
	return process_weather_user(userdata)

def update_user(user_data: dict) -> None:
	get_weather_user(user_data['username'])
	user_max = False if user_data['max']['disable'] else (None if user_data['max']['default'] else user_data['max']['value'])
	user_min = False if user_data['min']['disable'] else (None if user_data['min']['default'] else user_data['min']['value'])

	userdata = {
		'lat': user_data['lat'],
		'lon': user_data['lon'],
		'max': user_max,
		'min': user_min,
	}
	db.weather_users.update_one(
		{'_id': user_data['_id']},
		{'$set': userdata}
	)

	return process_weather_user(get_weather_user(user_data['username']))

def get_last_exec() -> dict|None:
	return db.weather_log.find_one({}, sort=[('timestamp', -1)])

def get_alert_history(username: str|None, start: int, count: int) -> list:
	selection = db.alert_history.find({} if username is None else {'to': username}, sort=[('_id', -1)])

	result = []
	for i in selection.limit(count).skip(start):
		result += [{
			'recipient': i['to'],
			'message': i['message'],
			'sent': i['_id'].generation_time,
		}]

	return result

def count_alert_history(username: str|None) -> list:
	return db.alert_history.count_documents({} if username is None else {'to': username})

def log_weather_alert(users: list[str], error: str|None) -> None:
	db.weather_log.insert_one({
		'timestamp': datetime.utcnow(),
		'users': users,
		'error': error,
	})

def log_user_weather_alert(username: str, message: str) -> None:
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
