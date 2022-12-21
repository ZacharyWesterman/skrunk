from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
import application.tags as tags

from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime
import mimetypes
import threading
import os

db = None
blob_path = None

def path(id: str, ext: str = '') -> str:
	global blob_path
	return f'{blob_path}/{id}{ext}'

def save_blob_data(file: object) -> str:
	global blob_path
	filename = file.filename
	id, ext = create_blob(filename)
	this_blob_path = path(id, ext)

	print(f'Beginning stream of file "{filename}"...')
	file.save(this_blob_path)
	print(f'Finished stream of file "{filename}".')

	size = os.stat(this_blob_path).st_size
	mark_as_completed(id, size)

	return id

def create_blob(name: str, tags: list = []) -> str:
	global db

	mime = mimetypes.guess_type(name)[0]
	if mime is None:
		mime = 'application/octet-stream'

	pos = name.rfind('.')
	ext = name[pos::] if pos > -1 else ''
	name = name[0:pos] if pos > -1 else name

	username = decode_user_token(get_request_token()).get('username')
	user_data = db.data.users.find_one({'username': username})

	if not user_data:
		raise exceptions.UserDoesNotExistError(username)

	auto_tags = [ i for i in mime.split('/') if i != 'application' ]

	return db.data.blob.insert_one({
		'created': datetime.utcnow(),
		'name': name,
		'ext': ext,
		'mimetype': mime,
		'size': 0,
		'tags': list(set(tags + auto_tags)),
		'creator': user_data['_id'],
		'complete': False,
	}).inserted_id, ext

def mark_as_completed(id: str, size: int) -> None:
	db.data.blob.update_one({'_id': ObjectId(id)}, {'$set': {'complete': True, 'size': size}})

def get_blobs(username: Optional[str], start: int, count: int, tagstr: Optional[str]) -> list:
	global db
	blobs = []
	mongo_tag_query = tags.parse(tagstr).output() if type(tagstr) is str else {}

	if username is None:
		selection = db.data.blob.find(mongo_tag_query, sort=[('created', -1)])
	else:
		user_data = db.data.users.find_one({'username': username})
		if not user_data:
			return []

		selection = db.data.blob.find({'$and': [{'creator': user_data['_id']}, mongo_tag_query]}, sort=[('created', -1)])

	for i in selection.limit(count).skip(start):
		user_data = db.data.users.find_one({'_id': i['creator']})
		i['creator'] = user_data['username'] if user_data else str(i['creator'])
		i['id'] = i['_id']
		blobs += [i]

	return blobs

def count_blobs(username: Optional[str], tagstr: Optional[str]) -> int:
	global db
	mongo_tag_query = tags.parse(tagstr).output() if type(tagstr) is str else {}

	if username is None:
		return db.data.blob.count_documents(mongo_tag_query)
	else:
		user_data = db.data.users.find_one({'username': username})
		if not user_data:
			return 0

		return db.data.blob.count_documents({'$and': [{'creator': user_data['_id']}, mongo_tag_query]})

def get_blob_data(blob_id: str) -> dict:
	global db
	blob_data = db.data.blob.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		user_data = db.data.users.find_one({'_id': blob_data['creator']})
		blob_data['creator'] = user_data['username'] if user_data else str(blob_data['creator'])
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
		return blob_data

	raise exceptions.BlobDoesNotExistError(blob_id)

def set_blob_tags(blob_id: str, tags: list) -> dict:
	global db
	blob_data = db.data.blob.find_one({'_id': ObjectId(blob_id)})
	if not blob_data:
		raise exceptions.BlobDoesNotExistError(blob_id)

	tags = [ i.lower() for i in list(set(tags)) ]

	db.data.blob.update_one({'_id': ObjectId(blob_id)}, {'$set': {'tags': tags}})
	blob_data['tags'] = tags
	return blob_data
