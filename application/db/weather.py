import application.exceptions as exceptions

import bcrypt

db = None

def get_users() -> list:
	global db
	users = [ user for user in db.weather.users.find({}) ]
	for i in users:
		i['username'] = i['_id']

	return sorted(users, key = lambda elem: str(int(elem['exclude']))+elem['username'])

def create_user(user_data: dict) -> None:
	global db

	userdata = db.weather.users.find_one({'_id': user_data['username']})

	if userdata:
		raise exceptions.UserExistsError(user_data["username"])
	else:
		userdata = {
			'_id': user_data['username'],
			'lat': user_data['lat'],
			'lon': user_data['lon'],
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
		userdata = {
			'lat': user_data['lat'],
			'lon': user_data['lon'],
			'phone': user_data['phone'],
		}
		db.weather.users.update_one(
			{'_id': user_data['username']},
			{'$set': userdata}
		)
	else:
		raise exceptions.UserDoesNotExistError(user_data["username"])

#May return None if weather alerts has never been run.
def get_last_exec() -> dict:
	global db

	last_exec = db.weather.log.find_one({}, sort=[('timestamp', -1)])
	return last_exec
