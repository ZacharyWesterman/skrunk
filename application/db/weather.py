import application.exceptions as exceptions

from pymongo import MongoClient
db: MongoClient = None

def get_users() -> list:
	global db
	users = [ user for user in db.weather.users.find({}) ]
	for i in users:
		i['username'] = i['_id']

		i['max'] = {
			'value': i.get('max') if type(i.get('max')) is float else 0.0,
			'default': i.get('max') is None,
			'disable': i.get('max') == False,
		}
		i['min'] = {
			'value': i.get('min') if type(i.get('min')) is float else 0.0,
			'default': i.get('min') is None,
			'disable': i.get('min') == False,
		}

	return sorted(users, key = lambda elem: str(int(elem['exclude']))+elem['username'])

def create_user(user_data: dict) -> None:
	global db

	userdata = db.weather.users.find_one({'_id': user_data['username']})

	if userdata:
		raise exceptions.UserExistsError(user_data["username"])
	else:
		user_max = False if user_data['max']['disable'] else (None if user_data['max']['default'] else user_data['max'])
		user_min = False if user_data['min']['disable'] else (None if user_data['min']['default'] else user_data['min'])

		userdata = {
			'_id': user_data['username'],
			'lat': user_data['lat'],
			'lon': user_data['lon'],
			'max': user_max,
			'min': user_min,
			'phone': user_data['phone'],
			'last_sent': None,
			'exclude': False,
		}
		db.weather.users.insert_one(userdata)

def delete_user(username: str) -> None:
	global db

	userdata = db.weather.users.find_one({'_id': username})

	if userdata:
		db.weather.users.delete_one({'_id': username})
	else:
		raise exceptions.UserDoesNotExistError(username)

def set_user_excluded(username: str, exclude: bool) -> dict:
	global db

	userdata = db.weather.users.find_one({'_id': username})

	if userdata:
		db.weather.users.update_one({'_id': username}, {'$set': {'exclude': exclude}})
		userdata['exclude'] = exclude
		return userdata
	else:
		raise exceptions.UserDoesNotExistError(username)

def update_user(user_data: dict) -> None:
	global db

	userdata = db.weather.users.find_one({'_id': user_data['username']})

	if userdata:
		user_max = False if user_data['max']['disable'] else (None if user_data['max']['default'] else user_data['max']['value'])
		user_min = False if user_data['min']['disable'] else (None if user_data['min']['default'] else user_data['min']['value'])

		userdata = {
			'lat': user_data['lat'],
			'lon': user_data['lon'],
			'max': user_max,
			'min': user_min,
			'phone': user_data['phone'],
		}
		db.weather.users.update_one(
			{'_id': user_data['username']},
			{'$set': userdata}
		)
	else:
		raise exceptions.UserDoesNotExistError(user_data["username"])

def get_last_exec() -> dict|None:
	global db

	last_exec = db.weather.log.find_one({}, sort=[('timestamp', -1)])
	return last_exec

def get_alert_history(start: int, count: int) -> list:
	selection = db.weather.alert_history.find({}, sort=[('_id', -1)])

	result = []
	for i in selection.limit(count).skip(start):
		result += [{
			'recipient': i['to'],
			'message': i['message'],
			'sent': i['_id'].generation_time,
		}]

	return result
