from application.integrations import google_books, exceptions

def resolve_search_books(_, info, title: str, author: str) -> dict:
	try:
		return { '__typename': 'BookList', 'books': google_books.query(title=title, author=author) }
	except exceptions.ApiFailedError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }
