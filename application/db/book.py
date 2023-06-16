from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
from . import users
from application.integrations import google_books
from typing import Optional

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
	if book_data['thumbnail'] is not None:
		book_data['thumbnail'] = book_data['thumbnail'].replace('http://', 'https://')

	return book_data

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
		**google_book_data,
	}

	db.insert_one(book_data)
	return book_data

def unlink_book_tag(rfid: str) -> dict:
	book_data = db.find_one({'rfid': rfid})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	db.delete_one({'rfid': rfid})
	return book_data

def get_books(owner: Optional[str], title: Optional[str], author: Optional[str], genre: Optional[str], start: int, count: int) -> list:
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

	selection = db.find({'$and': query} if len(query) else {}, sort = [('title', 1), ('authors', 1)])
	for i in selection.limit(count).skip(start):
		try:
			i['owner'] = users.get_user_by_id(i['owner'])['username']
		except exceptions.UserDoesNotExistError:
			pass

		i['id'] = i['_id']
		if i['thumbnail'] is not None:
			i['thumbnail'] = i['thumbnail'].replace('http://', 'https://')

		i['categories'] = i.get('categories', [])

		books += [i]

	return books

def count_books(owner: Optional[str], title: Optional[str], author: Optional[str], genre: Optional[str]) -> list:
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

	return db.count_documents({'$and': query} if len(query) else {})