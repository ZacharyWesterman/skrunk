"""application.resolvers.mutation.bugs"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.bugs import (comment_on_bug, delete_bug_report,
                                 get_bug_report, report_bug, set_bug_status)

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('reportBug')
@perms.module('bugs')
@perms.require('edit')
@handle_client_exceptions
def resolve_report_bug(_, _info: GraphQLResolveInfo, text: str, plaintext: bool) -> dict:
	"""
	Reports a bug or other feedback.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		text (str): The bug report text submitted by the user.
		plaintext (bool): Indicates if the bug report text is in plaintext format.
			If False, the text is assumed to be in Markdown format.

	Returns:
		dict: A dictionary representing the created bug report.
	"""
	return {'__typename': 'BugReport', **report_bug(text, plaintext)}


@mutation.field('deleteBug')
@perms.module('bugs')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_bug_report)
@handle_client_exceptions
def resolve_delete_bug(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Deletes a bug report by its ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the bug report to delete.

	Returns:
		dict: A dictionary representing the deleted bug report.
	"""
	return {'__typename': 'BugReport', **delete_bug_report(id)}


@mutation.field('setBugStatus')
@perms.module('bugs')
@perms.require('edit')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_bug_status(_, _info: GraphQLResolveInfo, id: str, status: bool) -> dict:
	"""
	Mark a bug report as resolved or unresolved.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the bug report to update.
		status (bool): The new resolution status to set for the bug report.

	Returns:
		dict: A dictionary representing the updated bug report.
	"""
	return {'__typename': 'BugReport', **set_bug_status(id, status)}


@mutation.field('commentOnBug')
@perms.module('bugs')
@perms.require('edit')
@handle_client_exceptions
def resolve_comment_on_bug(
	_,
    _info: GraphQLResolveInfo,
    id: str,
    text: str,
    plaintext: bool
) -> dict:
	"""
	Adds a comment to a bug report.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the bug report to comment on.
		text (str): The content of the comment to add.
		plaintext (bool): Indicates whether the comment text is in plain text format.
			If False, the text is assumed to be in Markdown format.

	Returns:
		dict: A dictionary representing the updated bug report.
	"""
	return {'__typename': 'BugReport', **comment_on_bug(id, text, plaintext)}
