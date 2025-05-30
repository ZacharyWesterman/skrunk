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
	return {'__typename': 'BugReport', **report_bug(text, plaintext)}


@mutation.field('deleteBug')
@perms.module('bugs')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_bug_report)
@handle_client_exceptions
def resolve_delete_bug(_, _info: GraphQLResolveInfo, id: str) -> dict:
	return {'__typename': 'BugReport', **delete_bug_report(id)}


@mutation.field('setBugStatus')
@perms.module('bugs')
@perms.require('edit')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_bug_status(_, _info: GraphQLResolveInfo, id: str, status: bool) -> dict:
	return {'__typename': 'BugReport', **set_bug_status(id, status)}


@mutation.field('commentOnBug')
@perms.module('bugs')
@perms.require('edit')
@handle_client_exceptions
def resolve_comment_on_bug(_, _info: GraphQLResolveInfo, id: str, text: str, plaintext: bool) -> dict:
	return {'__typename': 'BugReport', **comment_on_bug(id, text, plaintext)}
