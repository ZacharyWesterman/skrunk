from application.db.book import *
import application.exceptions as exceptions
from ariadne import convert_kwargs_to_snake_case
import application.db.perms as perms
from application.integrations.exceptions import ApiFailedError

@convert_kwargs_to_snake_case
def resolve_link_book_tag(_, info, rfid: str, book_id: str) -> dict:
	try:
		return { '__typename': 'BookTag', **link_book_tag(rfid, book_id) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
	except ApiFailedError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'], data_func = get_book_tag)
def resolve_unlink_book_tag(_, info, rfid: str) -> dict:
	try:
		return { '__typename': 'BookTag', **unlink_book_tag(rfid) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_share_book_with_user(_, info, id: str, username: str) -> dict:
	try:
		return { '__typename': 'Book', **share_book_with_user(id, username) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_share_book_with_non_user(_, info, id: str, name: str) -> dict:
	try:
		return { '__typename': 'Book', **share_book_with_non_user(id, name) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_borrow_book(_, info, id: str) -> dict:
	try:
		user_data = perms.caller_info(info)
		return { '__typename': 'Book', **borrow_book(id, user_data) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_return_book(_, info, id: str) -> dict:
	try:
		user_data = perms.caller_info(info)
		return { '__typename': 'Book', **return_book(id, user_data) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'], data_func = get_book)
def resolve_change_book_owner(_, info, id: str, username: str) -> dict:
	try:
		return { '__typename': 'Book', **set_book_owner(id, username) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'], data_func = get_book)
def resolve_edit_book(_, info, id: str, changes: dict) -> dict:
	try:
		return { '__typename': 'Book', **edit_book(id, changes) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_create_book(_, info, data: dict) -> dict:
	try:
		return { '__typename': 'BookTag', **create_book(data) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
