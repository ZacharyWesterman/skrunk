"""application.resolvers.mutation.book"""

from graphql.type import GraphQLResolveInfo

from application.db import notification, perms
from application.db.book import (append_ebook, borrow_book, create_book,
                                 edit_book, get_book, get_book_tag,
                                 link_book_tag, relink_book_tag, remove_ebook,
                                 return_book, set_book_owner,
                                 share_book_with_non_user,
                                 share_book_with_user, unlink_book_tag)
from application.db.users import get_user_by_id
from application.integrations.exceptions import ApiFailedError

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('linkBookTag')
@perms.module('books')
@perms.require('edit')
@handle_client_exceptions
def resolve_link_book_tag(_, _info: GraphQLResolveInfo, owner: str, rfid: str, bookId: str) -> dict:
	try:
		return {'__typename': 'BookTag', **link_book_tag(owner, rfid, bookId)}
	except ApiFailedError as e:
		return {'__typename': e.__class__.__name__, 'message': str(e)}


@mutation.field('unlinkBookTag')
@perms.module('books')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_book_tag)
@handle_client_exceptions
def resolve_unlink_book_tag(_, _info: GraphQLResolveInfo, rfid: str) -> dict:
	return {'__typename': 'BookTag', **unlink_book_tag(rfid)}


@mutation.field('shareBook')
@perms.module('books')
@perms.require('edit')
@handle_client_exceptions
def resolve_share_book_with_user(_, _info: GraphQLResolveInfo, id: str, username: str) -> dict:
	return {'__typename': 'Book', **share_book_with_user(id, username)}


@mutation.field('shareBookNonUser')
@perms.module('books')
@perms.require('edit')
@handle_client_exceptions
def resolve_share_book_with_non_user(_, _info: GraphQLResolveInfo, id: str, name: str) -> dict:
	return {'__typename': 'Book', **share_book_with_non_user(id, name)}


@mutation.field('borrowBook')
@perms.module('books')
@perms.require('edit')
@handle_client_exceptions
def resolve_borrow_book(_, _info: GraphQLResolveInfo, id: str) -> dict:
	user_data = perms.caller_info_strict()
	return {'__typename': 'Book', **borrow_book(id, user_data)}


@mutation.field('requestToBorrowBook')
@perms.module('books')
@perms.require('edit')
@handle_client_exceptions
def resolve_request_borrow_book(_, _info: GraphQLResolveInfo, id: str) -> dict:
	user_data = perms.caller_info_strict()
	book_data = get_book(id)
	owner_data = get_user_by_id(book_data['owner'])

	user = user_data['display_name']
	title = book_data['title']
	authors = ','.join(book_data['authors'])

	notification.send(
		title=f'{user} wants to borrow a book!',
		body=f'{user} would like to borrow "{title}" by {authors}. Remember to talk to them and let them know what you think!',
		username=owner_data['username'],
		category='books',
	)

	return {'__typename': 'Notification', 'message': 'Notification sent'}


@mutation.field('returnBook')
@perms.module('books')
@perms.require('edit')
@handle_client_exceptions
def resolve_return_book(_, _info: GraphQLResolveInfo, id: str) -> dict:
	user_data = perms.caller_info_strict()
	return {'__typename': 'Book', **return_book(id, user_data)}


@mutation.field('setBookOwner')
@perms.module('books')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_book)
@handle_client_exceptions
def resolve_change_book_owner(_, _info: GraphQLResolveInfo, id: str, username: str) -> dict:
	return {'__typename': 'Book', **set_book_owner(id, username)}


@mutation.field('editBook')
@perms.module('books')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_book)
@handle_client_exceptions
def resolve_edit_book(_, _info: GraphQLResolveInfo, id: str, changes: dict) -> dict:
	return {'__typename': 'Book', **edit_book(id, changes)}


@mutation.field('createBook')
@perms.module('books')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_book(_, _info: GraphQLResolveInfo, owner: str, data: dict) -> dict:
	return {'__typename': 'BookTag', **create_book(owner, data)}


@mutation.field('appendEBook')
@perms.module('books')
@perms.require('admin')
@handle_client_exceptions
def resolve_append_ebook(_, _info: GraphQLResolveInfo, id: str, url: str) -> dict:
	return {'__typename': 'Book', **append_ebook(id, url)}


@mutation.field('removeEBook')
@perms.module('books')
@perms.require('admin')
@handle_client_exceptions
def resolve_remove_ebook(_, _info: GraphQLResolveInfo, id: str, index: int) -> dict:
	return {'__typename': 'Book', **remove_ebook(id, index)}


@mutation.field('relinkBookTag')
@perms.module('books')
@perms.require('admin', perform_on_self=True, data_func=get_book)
@handle_client_exceptions
def resolve_relink_book_tag(_, _info: GraphQLResolveInfo, id: str, rfid: str) -> dict:
	"""
	Change the RFID of a book tag to a new one.

	Args:
		id (str): The ID of the book.
		rfid (str): The new RFID for the book tag.

	Returns:
		dict: The updated book information.
	"""
	return {'__typename': 'Book', **relink_book_tag(id, rfid)}
