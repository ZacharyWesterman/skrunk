from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
from . import users

db = None

def get_book_tag(rfid: str) -> dict:
	book_data = db.find_one({'rfid': rfid})

	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	return book_data

def link_book_tag(rfid: str, book_id: str) -> dict:
	if db.find_one({'rfid': rfid}):
		raise exceptions.BookTagExistsError(rfid)

	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	book_data = {
		'rfid': rfid,
		'bookId': book_id,
		'creator': user_data['_id'],
	}

	db.insert_one(book_data)
	return book_data

def unlink_book_tag(rfid: str) -> dict:
	book_data = db.find_one({'rfid': rfid})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	db.delete_one({'rfid': rfid})
	return book_data
