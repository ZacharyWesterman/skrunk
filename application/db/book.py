from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
from . import users
from application.integrations import google_books
from typing import Optional
from datetime import datetime
from bson.objectid import ObjectId

db = None

def get_book_tag(rfid: str) -> dict:
	book_data = db.find_one({'rfid': rfid})

	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	try:
		book_data['owner'] = users.get_user_by_id(book_data['owner'])['username']
	except exceptions.UserDoesNotExistError:
		pass

	book_data['id'] = book_data['_id']

	return book_data

def next_out_of_date_book_rfid(before: datetime) -> str:
	book_data = db.find_one({'lastSync': {'$lt': before}})
	if book_data is None:
		return None

	return book_data['rfid']

def refresh_book_data(rfid: str) -> None:
	book_data = db.find_one({'rfid': rfid})

	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(rfid)

	google_book_data = google_books.get(id = book_data['bookId'])

	fields = ['title', 'subtitle', 'authors', 'publisher', 'publishedDate', 'description', 'industryIdentifiers', 'pageCount', 'categories', 'maturityRating', 'language', 'thumbnail']
	updated = {'lastSync': datetime.utcnow()}
	for i in fields:
		if i in book_data.get('noSyncFields', []):
			continue

		new_val = google_book_data.get(i)
		if new_val != book_data[i]:
			updated[i] = new_val

	db.update_one({'rfid': rfid}, {'$set': updated})


def link_book_tag(rfid: str, book_id: str) -> dict:
	if db.find_one({'rfid': rfid}):
		raise exceptions.BookTagExistsError(rfid)

	google_book_data = google_books.get(id = book_id)
	del google_book_data['id']

	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	book_data = {
		'rfid': rfid,
		'bookId': book_id,
		'creator': user_data['_id'],
		'owner': user_data['_id'],
		'shared': False,
		'shareHistory': [],
		'lastSync': datetime.utcnow(),
		'created': datetime.utcnow(),
		'noSyncFields': [],
	}
	fields = ['title', 'subtitle', 'authors', 'publisher', 'publishedDate', 'description', 'industryIdentifiers', 'pageCount', 'categories', 'maturityRating', 'language', 'thumbnail']
	for i in fields:
		book_data[i] = google_book_data.get(i)

	db.insert_one(book_data)
	return book_data

def unlink_book_tag(rfid: str) -> dict:
	book_data = db.find_one({'rfid': rfid})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	db.delete_one({'rfid': rfid})
	return book_data

def get_books(owner: Optional[str], title: Optional[str], author: Optional[str], genre: Optional[str], shared: Optional[bool], start: int, count: int) -> list:
	global db
	books = []
	query = []
	if owner is not None:
		try:
			user_data = users.get_user_data(owner)
			query += [{'creator': user_data['_id']}]
		except exceptions.UserDoesNotExistError:
			return []

	if title is not None:
		query += [{'title': {'$regex': title, '$options': 'i'}}]

	if author is not None:
		query += [{'authors': {'$regex': author, '$options': 'i'}}]

	if genre is not None:
		query += [{'categories': {'$regex': genre, '$options': 'i'}}]

	if shared is not None:
		query += [{'shared': shared}]

	selection = db.find({'$and': query} if len(query) else {}, sort = [('title', 1), ('authors', 1)])
	for i in selection.limit(count).skip(start):
		try:
			i['owner'] = users.get_user_by_id(i['owner'])['username']
		except exceptions.UserDoesNotExistError:
			pass

		i['id'] = i['_id']

		cat = []
		for k in i.get('categories', []):
			cat += k.split(' / ')
		i['categories'] = sorted(list(set(cat)))

		books += [i]

	return books

def count_books(owner: Optional[str], title: Optional[str], author: Optional[str], genre: Optional[str], shared: Optional[bool]) -> list:
	global db
	query = []
	if owner is not None:
		try:
			user_data = users.get_user_data(owner)
			query += [{'creator': user_data['_id']}]
		except exceptions.UserDoesNotExistError:
			return 0

	if title is not None:
		query += [{'title': {'$regex': title, '$options': 'i'}}]

	if author is not None:
		query += [{'authors': {'$regex': author, '$options': 'i'}}]

	if genre is not None:
		query += [{'categories': {'$regex': genre, '$options': 'i'}}]

	if shared is not None:
		query += [{'shared': shared}]

	return db.count_documents({'$and': query} if len(query) else {})

def share_book_with_user(book_id: str, username: str) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	user_data = users.get_user_data(username)

	if len(book_data['shareHistory']):
		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_id}, {'$set': updates})
	db.update_one({'_id': book_id}, {'$push': {'shareHistory': {
		'user_id': user_data['_id'],
		'name': username,
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data

def share_book_with_non_user(book_id: str, name: str) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if len(book_data['shareHistory']):
		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_id}, {'$set': updates})
	db.update_one({'_id': book_id}, {'$push': {'shareHistory': {
		'user_id': None,
		'name': name,
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data

def borrow_book(book_id: str, user_data: dict) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if len(book_data['shareHistory']):
		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_id}, {'$set': updates})
	db.update_one({'_id': book_id}, {'$push': {'shareHistory': {
		'user_id': user_data['_id'],
		'name': user_data['username'],
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data

def return_book(book_id: str, user_data: dict) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if len(book_data['shareHistory']) == 0:
		raise exceptions.BookCannotBeShared('Nobody is borrowing this book.')

	last_share = len(book_data['shareHistory']) - 1
	print(book_data['owner'], flush=True)
	print(user_data['_id'], flush=True)
	if book_data['shareHistory'][-1]['user_id'] != user_data['_id'] and book_data['owner'] != user_data['_id']:
		raise exceptions.BookCannotBeShared('You did not borrow this book.')

	db.update_one({'_id': book_id}, {'$set': {'shared': False, f'shareHistory.{last_share}.stop': datetime.utcnow()}})
	return book_data