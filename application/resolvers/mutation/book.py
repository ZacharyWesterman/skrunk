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