from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
import application.tags as tags
from . import users

from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime
from zipfile import ZipFile
import mimetypes
import threading
import pathlib
import uuid
import os

db = None
blob_path = None

def path(id: str, ext: str = '') -> str:
	global blob_path
	return f'{blob_path}/{id}{ext}'

def save_blob_data(file: object, auto_unzip: bool) -> str:
	global blob_path
	filename = file.filename
	id, ext = create_blob(filename)
	this_blob_path = path(id, ext)

	print(f'Beginning stream of file "{filename}"...')
	file.save(this_blob_path)
	print(f'Finished stream of file "{filename}".')

	if auto_unzip and ext == '.zip':
		print(f'Unzipping file "{filename}"...')
		extract_count = 0
		with ZipFile(this_blob_path, 'r') as fp:
			for name in fp.namelist():
				#directly create new blobs from each item in the zip file
				id2, ext2 = create_blob(name)
				inner_blob_path = path(id2, ext2)
				with fp.open(name, 'r') as input:
					with open(inner_blob_path, 'wb') as output:
						output.write(input.read())
				size = os.stat(inner_blob_path).st_size
				mark_as_completed(id2, size)
				extract_count += 1

		print(f'Finished unzipping "{filename}" (extracted {extract_count} files).')
		delete_blob(id)
	else:
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
	user_data = users.get_user_data(username)

	auto_tags = [ i for i in mime.split('/') if i != 'application' ]

	return db.insert_one({
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
	db.update_one({'_id': ObjectId(id)}, {'$set': {'complete': True, 'size': size}})

def get_blobs(username: Optional[str], start: int, count: int, tagstr: Optional[str], begin_date: Optional[datetime], end_date: Optional[datetime]) -> list:
	global db
	blobs = []
	mongo_tag_query = tags.parse(tagstr).output() if type(tagstr) is str else {}

	query = [ mongo_tag_query ] if mongo_tag_query != {} else []

	if username is not None:
		try:
			user_data = users.get_user_data(username)
			query += [{'creator': user_data['_id']}]
		except exceptions.UserDoesNotExistError:
			return 0

	if begin_date is not None:
		query += [{'created': {'$gte': begin_date}}]
	if end_date is not None:
		query += [{'created': {'$lte': end_date}}]

	selection = db.find({'$and': query} if len(query) else {}, sort=[('created', -1)])
	for i in selection.limit(count).skip(start):
		i['id'] = i['_id']
		try:
			user_data = users.get_user_by_id(i['creator'])
			i['creator'] = user_data['username']
		except exceptions.UserDoesNotExistError:
			i['creator'] = str(i['creator'])
		blobs += [i]

	return blobs

def count_blobs(username: Optional[str], tagstr: Optional[str], begin_date: Optional[datetime], end_date: Optional[datetime]) -> int:
	global db
	mongo_tag_query = tags.parse(tagstr).output() if type(tagstr) is str else {}

	query = [ mongo_tag_query ] if mongo_tag_query != {} else []

	if username is not None:
		try:
			user_data = users.get_user_data(username)
			query += [{'creator': user_data['_id']}]
		except exceptions.UserDoesNotExistError:
			return 0

	if begin_date is not None:
		query += [{'created': {'$gte': begin_date}}]
	if end_date is not None:
		query += [{'created': {'$lte': end_date}}]

	return db.count_documents({'$and': query} if len(query) else {})

def get_blob_data(blob_id: str) -> dict:
	global db
	blob_data = db.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		blob_data['id'] = blob_data['_id']
		try:
			user_data = users.get_user_by_id(blob_data['creator'])
			blob_data['creator'] = user_data['username']
		except exceptions.UserDoesNotExistError:
			blob_data['creator'] = str(blob_data['creator'])
	return blob_data

def delete_blob(blob_id: str) -> bool:
	global db
	blob_data = db.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		try:
			os.remove(path(blob_id, blob_data['ext']))
		except FileNotFoundError:
			pass
		db.delete_one({'_id': ObjectId(blob_id)})
		return blob_data

	raise exceptions.BlobDoesNotExistError(blob_id)

def set_blob_tags(blob_id: str, tags: list) -> dict:
	global db
	blob_data = db.find_one({'_id': ObjectId(blob_id)})
	if not blob_data:
		raise exceptions.BlobDoesNotExistError(blob_id)

	tags = [ i.lower() for i in list(set(tags)) ]

	db.update_one({'_id': ObjectId(blob_id)}, {'$set': {'tags': tags}})
	blob_data['tags'] = tags
	return blob_data
