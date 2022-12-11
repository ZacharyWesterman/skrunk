from datetime import datetime
import mimetypes
from application.tokens import decode_user_token, get_request_token
import os
from bson.objectid import ObjectId

db = None
blob_path = None

def path(id: str, ext: str = None) -> str:
	global blob_path
	return f'{blob_path}/{id}.{ext}' if ext is not None else f'{blob_path}/{id}'

def create_blob(dir: str, name: str, tags: list = []) -> str:
	global db
	pos = name.rfind('.')
	ext = name[pos+1::]

	username = decode_user_token(get_request_token()).get('username')
	mime = mimetypes.guess_type(name)[0]
	if mime is None:
		mime = 'application/octet-stream'

	return db.data.blob.insert_one({
		'created': datetime.utcnow(),
		'name': name[0:pos],
		'ext': ext,
		'mimetype': mime,
		'tags': tags,
		'creator': username,
	}).inserted_id, ext

def get_user_blobs(username: str, start: int, count: int) -> list:
	global db
	blobs = []
	for i in db.data.blob.find({'creator': username}, sort=[('created', -1)]).limit(count).skip(start):
		i['id'] = i['_id']
		blobs += [i]

	return blobs

def get_all_blobs(start: int, count: int) -> list:
	global db
	blobs = []
	for i in db.data.blob.find({}, sort=[('created', -1)]).limit(count).skip(start):
		i['id'] = i['_id']
		blobs += [i]

	return blobs

def count_user_blobs(username: str) -> int:
	global db
	return db.data.blob.count_documents({'creator': username})

def count_all_blobs() -> int:
	global db
	return db.data.blob.count_documents({})

def get_blob_data(blob_id: str) -> dict:
	global db
	blob_data = db.data.blob.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		blob_data['id'] = blob_data['_id']
	return blob_data

def delete_blob(blob_id: str) -> bool:
	global db
	blob_data = db.data.blob.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		try:
			os.remove(path(blob_id, blob_data['ext']))
		except FileNotFoundError:
			pass
		db.data.blob.delete_one({'_id': ObjectId(blob_id)})
		return True

	return False
