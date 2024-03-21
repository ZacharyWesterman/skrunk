from application.db.book import *
import application.exceptions as exceptions
import application.db.perms as perms
from application.integrations.exceptions import ApiFailedError

@perms.require(['edit'])
def resolve_link_book_tag(_, info, rfid: str, bookId: str) -> dict:
	try:
		return { '__typename': 'BookTag', **link_book_tag(rfid, bookId) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
	except ApiFailedError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True, data_func = get_book_tag)
def resolve_unlink_book_tag(_, info, rfid: str) -> dict:
	try:
		return { '__typename': 'BookTag', **unlink_book_tag(rfid) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_share_book_with_user(_, info, id: str, username: str) -> dict:
	try:
		return { '__typename': 'Book', **share_book_with_user(id, username) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_share_book_with_non_user(_, info, id: str, name: str) -> dict:
	try:
		return { '__typename': 'Book', **share_book_with_non_user(id, name) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_borrow_book(_, info, id: str) -> dict:
	try:
		user_data = perms.caller_info()
		return { '__typename': 'Book', **borrow_book(id, user_data) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_return_book(_, info, id: str) -> dict:
	try:
		user_data = perms.caller_info()
		return { '__typename': 'Book', **return_book(id, user_data) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True, data_func = get_book)
def resolve_change_book_owner(_, info, id: str, username: str) -> dict:
	try:
		return { '__typename': 'Book', **set_book_owner(id, username) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True, data_func = get_book)
def resolve_edit_book(_, info, id: str, changes: dict) -> dict:
	try:
		return { '__typename': 'Book', **edit_book(id, changes) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_create_book(_, info, data: dict) -> dict:
	try:
		return { '__typename': 'BookTag', **create_book(data) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'])
def resolve_append_ebook(_, info, id: str, url: str) -> dict:
	try:
		return { '__typename': 'Book', **append_ebook(id, url) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
