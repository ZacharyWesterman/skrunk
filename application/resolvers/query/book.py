"""application.resolvers.query.book"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.book import (count_all_user_books, count_books, get_book,
                                 get_book_tag, get_books)
from application.db.users import userids_in_groups
from application.exceptions import BookTagDoesNotExistError
from application.integrations import google_books
from application.integrations.exceptions import ApiFailedError
from application.types import BookSearchFilter, Sorting

from ..decorators import handle_client_exceptions
from . import query


@query.field('searchBooks')
@perms.module('books')
def resolve_search_google_books(_, _info: GraphQLResolveInfo, title: str, author: str) -> dict:
	"""
	Resolves a search query for books using the Google Books API.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		title (str): The title of the book to search for.
		author (str): The author of the book to search for.

	Returns:
		dict: A dictionary with either:
			- '__typename': 'BookList' and 'books': list of found books, or
			- '__typename': error class name and 'message': error details if the API call fails.
	"""
	try:
		return {'__typename': 'BookList', 'books': google_books.query(title=title, author=author)}
	except ApiFailedError as e:
		return {'__typename': e.__class__.__name__, 'message': str(e)}


@query.field('getBookByTag')
@perms.module('books')
@handle_client_exceptions
def resolve_get_book_by_tag(_, _info: GraphQLResolveInfo, rfid: str) -> dict:
	"""
	Resolves a query to retrieve book information by RFID tag.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		rfid (str): The RFID tag identifier for the book.

	Returns:
		dict: A dictionary containing book information.
	"""
	tag_data = get_book_tag(rfid, parse=True)
	return {'__typename': 'Book', **tag_data}


@query.field('getBooks')
@perms.module('books')
def resolve_get_books(_, _info: GraphQLResolveInfo, filter: BookSearchFilter, start: int, count: int, sorting: Sorting) -> list:
	"""
	Resolves the retrieval of books based on provided filters, pagination, and sorting options.

	If the 'owner' field is not specified in the filter, it is set to the list of user IDs
	belonging to the caller's groups. This ensures that the count is scoped to the books
	owned by users in the caller's groups.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (BookSearchFilter): Dictionary of search filters to apply to the book query.
		start (int): The starting index for pagination.
		count (int): The number of books to retrieve.
		sorting (Sorting): Sorting options for the book query.

	Returns:
		list: A list of books matching the specified criteria.
	"""
	if filter.get('owner') is None:
		user_data = perms.caller_info_strict()
		groups = user_data.get('groups', [])
		if len(groups):
			filter['owner'] = userids_in_groups(groups)  # type: ignore[assignment]

	return get_books(filter, start, count, sorting)


@query.field('countBooks')
@perms.module('books')
def resolve_count_books(_, _info: GraphQLResolveInfo, filter: BookSearchFilter) -> int:
	"""
	Resolves the total count of books matching the given filter.

	If the 'owner' field is not specified in the filter, it is set to the list of user IDs
	belonging to the caller's groups. This ensures that the count is scoped to the books
	owned by users in the caller's groups.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (BookSearchFilter): Dictionary containing search filters for books.

	Returns:
		int: The number of books matching the filter criteria.
	"""
	if filter.get('owner') is None:
		user_data = perms.caller_info_strict()
		groups = user_data.get('groups', [])
		if len(groups):
			filter['owner'] = userids_in_groups(groups)  # type: ignore[assignment]

	return count_books(filter)


@query.field('countAllUserBooks')
@perms.module('books')
def resolve_count_all_user_books(_, _info: GraphQLResolveInfo) -> list:
	"""
	Resolves the total count of books for all users in the caller's groups.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: The result of counting all user books for users in the caller's groups.
	"""
	user_data = perms.caller_info_strict()
	users = userids_in_groups(user_data.get('groups', []))
	return count_all_user_books(users if len(users) else None)


@query.field('getBookDescription')
@perms.module('books')
def resolve_get_book_description(_, _info: GraphQLResolveInfo, id: str) -> str | None:
	"""
	Resolves the description of a book by its ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the book.

	Returns:
		str | None: The description of the book if found, otherwise None.
	"""
	try:
		book_data = get_book(id)
	except BookTagDoesNotExistError:
		return None

	return book_data.get('description')
