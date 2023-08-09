from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
from application.objects import BookSearchFilter
from . import users
from application.integrations import google_books
from datetime import datetime
from bson.objectid import ObjectId
import re

db = None

def process_share_hist(share_history: list) -> list:
	share_hist = []
	for hist in share_history:
		if hist['user_id'] == None:
			hist['display_name'] = hist['name']
		else:
			try:
				shared_with = users.get_user_by_id(hist['user_id'])
			except exceptions.UserDoesNotExistError:
				shared_with = None

			hist['display_name'] = shared_with['display_name'] if shared_with is not None else hist['name']

		share_hist += [hist]

	return share_hist

def process_book_tag(book_data: dict) -> dict:
	try:
		userdata = users.get_user_by_id(book_data['owner'])
		book_data['owner'] = userdata
	except exceptions.UserDoesNotExistError:
		book_data['owner'] = {
			'username': book_data['owner'],
			'display_name': book_data['owner'],
		}

	book_data['shareHistory'] = process_share_hist(book_data['shareHistory'])
	book_data['id'] = book_data['_id']
	return book_data

def get_book_tag(rfid: str, *, parse: bool = False) -> dict:
	book_data = db.find_one({'rfid': rfid})

	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	return process_book_tag(book_data) if parse else book_data

def get_book(id: str, *, parse: bool = False) -> dict:
	book_data = db.find_one({'_id': ObjectId(id)})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(id)

	return process_book_tag(book_data) if parse else book_data

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

	book_data['owner'] = user_data
	book_data['shareHistory'] = process_share_hist(book_data['shareHistory'])

	return book_data

def unlink_book_tag(rfid: str) -> dict:
	book_data = db.find_one({'rfid': rfid})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	db.delete_one({'rfid': rfid})
	return book_data

def build_book_query(filter: BookSearchFilter) -> dict:
	query = []
	if filter.get('owner') is not None:
		user_data = users.get_user_data(filter.get('owner'))
		query += [{'owner': user_data['_id']}]

	if filter.get('title') is not None:
		isbn = filter.get('title').strip().replace('-', '')
		if re.match(r'^\d{9,13}$', isbn):
			query += [{'industryIdentifiers.identifier': isbn}]
		else:
			query += [{'title': {'$regex': filter.get('title'), '$options': 'i'}}]

	if filter.get('author') is not None:
		query += [{'authors': {'$regex': filter.get('author'), '$options': 'i'}}]

	if filter.get('genre') is not None:
		query += [{'categories': {'$regex': filter.get('genre'), '$options': 'i'}}]

	if filter.get('shared') is not None:
		query += [{'shared': filter.get('shared')}]

	return {'$and': query} if len(query) else {}

def get_books(filter: BookSearchFilter, start: int, count: int) -> list:
	global db
	books = []

	try:
		query = build_book_query(filter)
	except exceptions.UserDoesNotExistError:
		return []

	selection = db.find(query, sort = [('title', 1), ('authors', 1)])
	for i in selection.limit(count).skip(start):
		try:
			userdata = users.get_user_by_id(i['owner'])
			i['owner'] = userdata
		except exceptions.UserDoesNotExistError:
			i['owner'] = {
				'username': i['owner'],
				'display_name': i['owner'],
			}

		i['id'] = i['_id']
		i['shareHistory'] = process_share_hist(i['shareHistory'])

		cat = []
		for k in i.get('categories', []):
			cat += k.split(' / ')
		i['categories'] = sorted(list(set(cat)))

		books += [i]

	return books

def count_books(filter: BookSearchFilter) -> list:
	global db
	try:
		query = build_book_query(filter)
	except exceptions.UserDoesNotExistError:
		return 0

	return db.count_documents(query)

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

	if not book_data['shared']:
		raise exceptions.BookCannotBeShared('Nobody is borrowing this book.')

	last_share = len(book_data['shareHistory']) - 1
	print(book_data['owner'], flush=True)
	print(user_data['_id'], flush=True)
	if book_data['shareHistory'][-1]['user_id'] != user_data['_id'] and book_data['owner'] != user_data['_id']:
		raise exceptions.BookCannotBeShared('You did not borrow this book.')

	db.update_one({'_id': book_id}, {'$set': {'shared': False, f'shareHistory.{last_share}.stop': datetime.utcnow()}})
	return book_data

def set_book_owner(id: str, username: str) -> dict:
	book_data = get_book(id, parse = True)
	user_data = users.get_user_data(username)

	owner_hist = book_data.get('ownerHistory', [])
	if len(owner_hist):
		owner_hist[-1]['stop'] = datetime.utcnow()
	else:
		owner_hist = [{
			'user_id': book_data['owner'],
			'start': book_data['created'],
			'stop': datetime.utcnow(),
		}]
	owner_hist += [{
		'user_id': user_data['_id'],
		'start': datetime.utcnow(),
		'stop': None,
	}]

	book_data['owner'] = user_data['_id']

	db.update_one({'_id': ObjectId(id)}, {'$set': {'owner': user_data['_id']}})

	return book_data