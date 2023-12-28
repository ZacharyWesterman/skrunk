import random, string

db = None

def valid_api_key(key: str) -> bool:
	return True if db.find_one({'key': key}) else False

def new_api_key(description: str) -> str:
	#Generate random 30-digit API key. This probably will not clash with an existing key.
	api_key = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))

	db.insert_one({
		'key': api_key,
		'description': description,
	})

	return api_key

def delete_api_key(key: str) -> bool:
	return True if db.delete_one({'key': key}).deleted_count else False

def get_api_keys() -> list:
	#Should never have this many API keys floating around, but just in case.
	return [i for i in db.find().limit(200)]
