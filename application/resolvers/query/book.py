"""application.resolvers.query.book"""

from graphql.type import GraphQLResolveInfo

import application.db.perms as perms
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
	try:
		return {'__typename': 'BookList', 'books': google_books.query(title=title, author=author)}
	except ApiFailedError as e:
		return {'__typename': e.__class__.__name__, 'message': str(e)}


@query.field('getBookByTag')
@perms.module('books')
@handle_client_exceptions
def resolve_get_book_by_tag(_, _info: GraphQLResolveInfo, rfid: str) -> dict:
	tag_data = get_book_tag(rfid, parse=True)
	return {'__typename': 'Book', **tag_data}


@query.field('getBooks')
@perms.module('books')
def resolve_get_books(_, _info: GraphQLResolveInfo, filter: BookSearchFilter, start: int, count: int, sorting: Sorting) -> list:
	if filter.get('owner') is None:
		user_data = perms.caller_info_strict()
		groups = user_data.get('groups', [])
		if len(groups):
			filter['owner'] = userids_in_groups(groups)

	return get_books(filter, start, count, sorting)


@query.field('countBooks')
@perms.module('books')
def resolve_count_books(_, _info: GraphQLResolveInfo, filter: BookSearchFilter) -> int:
	if filter.get('owner') is None:
		user_data = perms.caller_info()
		groups = user_data.get('groups', [])
		if len(groups):
			filter['owner'] = userids_in_groups(groups)

	return count_books(filter)


@query.field('countAllUserBooks')
@perms.module('books')
def resolve_count_all_user_books(_, _info: GraphQLResolveInfo) -> list:
	user_data = perms.caller_info()
	users = userids_in_groups(user_data.get('groups', []))
	return count_all_user_books(users if len(users) else None)


@query.field('getBookDescription')
@perms.module('books')
def resolve_get_book_description(_, _info: GraphQLResolveInfo, id: str) -> str | None:
	try:
		book_data = get_book(id)
	except BookTagDoesNotExistError:
		return None

	return book_data.get('description')
