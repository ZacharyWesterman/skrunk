from datetime import datetime
import mimetypes
from application.tokens import decode_user_token, get_request_token
import os

db = None
blob_path = None

def path(id: str, ext: str) -> str:
	global blob_path
	return f'{blob_path}/{id}.{ext}'

def create_blob(dir: str, name: str, tags: list = []) -> str:
	global db
	pos = name.rfind('.')
	ext = name[pos+1::]

	username = decode_user_token(get_request_token()).get('username')

	return db.data.blob.insert_one({
		'created': datetime.now(),
		'name': name[0:pos],
		'ext': ext,
		'mimetype': mimetypes.guess_type(name)[0],
		'tags': tags,
		'creator': username,
	}).inserted_id, ext

def get_user_blobs(username: str, start: int, count: int) -> list:
	global db
	blobs = []
	for i in db.data.blob.find({'creator': username}).limit(count).skip(start):
		i['id'] = i['_id']
		blobs += [i]

	return blobs

def count_user_blobs(username: str) -> int:
	global db
	return db.data.blob.count_documents({'creator': username})

def delete_blob(blob_id: str) -> bool:
	global db
	blob_data = db.data.blob.find_one({'_id': blob_id})
	if blob_data:
		os.remove(path(blob_id, blob_data['ext']))
		db.data.blob.delete_one({'_id': blob_id})
		return True

	return False
