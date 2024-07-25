from application.integrations.exceptions import ApiFailedError
from application.integrations import google_books
from application.db.book import get_book_tag, get_books, count_books, count_all_user_books
from application.objects import BookSearchFilter, Sorting
import application.db.perms as perms
from application.db.users import userids_in_groups
from ..decorators import *

def resolve_search_google_books(_, info, title: str, author: str) -> dict:
	try:
		return { '__typename': 'BookList', 'books': google_books.query(title=title, author=author) }
	except ApiFailedError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }

@handle_client_exceptions
def resolve_get_book_by_tag(_, info, rfid: str) -> dict:
	tag_data = get_book_tag(rfid, parse = True)
	return { '__typename': 'Book', **tag_data }

def resolve_get_books(_, info, filter: BookSearchFilter, start: int, count: int, sorting: Sorting) -> list:
	if filter.get('owner') is None:
		user_data = perms.caller_info()
		groups = user_data.get('groups', [])
		if len(groups):
			filter['owner'] = userids_in_groups(groups)

	return get_books(filter, start, count, sorting)

def resolve_count_books(_, info, filter: BookSearchFilter) -> int:
	if filter.get('owner') is None:
		user_data = perms.caller_info()
		groups = user_data.get('groups', [])
		if len(groups):
			filter['owner'] = userids_in_groups(groups)

	return count_books(filter)

def resolve_count_all_user_books(_, info) -> list:
	user_data = perms.caller_info()
	users = userids_in_groups(user_data.get('groups', []))
	return count_all_user_books(users if len(users) else None)
