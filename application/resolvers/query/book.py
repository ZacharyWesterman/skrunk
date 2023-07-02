from application.integrations.exceptions import ApiFailedError
from application.integrations import google_books
from application.db.book import get_book_tag, get_books, count_books
from application.exceptions import ClientError
from typing import Optional

def resolve_search_google_books(_, info, title: str, author: str) -> dict:
	try:
		return { '__typename': 'BookList', 'books': google_books.query(title=title, author=author) }
	except ApiFailedError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }

def resolve_get_book_by_tag(_, info, rfid: str) -> dict:
	try:
		tag_data = get_book_tag(rfid)
		return { '__typename': 'Book', **tag_data }
	except ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_get_books(_, info, owner: Optional[str], title: Optional[str], author: Optional[str], genre: Optional[str], shared: Optional[bool], start: int, count: int) -> list:
	return get_books(
		title = title,
		author = author,
		genre = genre,
		owner = owner,
		start = start,
		count = count,
		shared = shared
	)

def resolve_count_books(_, info, owner: Optional[str], title: Optional[str], author: Optional[str], genre: Optional[str], shared: Optional[bool]) -> int:
	return count_books(
		title = title,
		author = author,
		genre = genre,
		owner = owner,
		shared = shared
	)