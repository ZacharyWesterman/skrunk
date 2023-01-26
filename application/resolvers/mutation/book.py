from application.db.book import link_book_tag
import application.exceptions as exceptions
from ariadne import convert_kwargs_to_snake_case

@convert_kwargs_to_snake_case
def resolve_link_book_tag(_, info, rfid: str, book_id: str) -> dict:
	try:
		return { '__typename': 'BookTag', **link_book_tag(rfid, book_id) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
