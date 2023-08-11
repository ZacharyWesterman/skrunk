from application.integrations.exceptions import ApiFailedError
from application.integrations import google_books
from application.db.book import get_book_tag, get_books, count_books
from application.exceptions import ClientError
from application.objects import BookSearchFilter

def resolve_search_google_books(_, info, title: str, author: str) -> dict:
	try:
		return { '__typename': 'BookList', 'books': google_books.query(title=title, author=author) }
	except ApiFailedError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }

def resolve_get_book_by_tag(_, info, rfid: str) -> dict:
	try:
		tag_data = get_book_tag(rfid, parse = True)
		return { '__typename': 'Book', **tag_data }
	except ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_get_books(_, info, filter: BookSearchFilter, start: int, count: int) -> list:
	return get_books(filter, start, count)

def resolve_count_books(_, info, filter: BookSearchFilter) -> int:
	return count_books(filter)