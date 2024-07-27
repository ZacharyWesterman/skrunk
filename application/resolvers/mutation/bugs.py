from application.db.bugs import *
import application.db.perms as perms
from ..decorators import *

@perms.module('bugs')
@perms.require('edit')
@handle_client_exceptions
def resolve_report_bug(_, info, text: str, plaintext: bool) -> dict:
	return { '__typename': 'BugReport', **report_bug(text, plaintext) }

@perms.module('bugs')
@perms.require('edit')
@perms.require('admin', perform_on_self = True, data_func = get_bug_report)
@handle_client_exceptions
def resolve_delete_bug(_, info, id: str) -> dict:
	return { '__typename': 'BugReport', **delete_bug_report(id) }

@perms.module('bugs')
@perms.require('edit')
@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_set_bug_status(_, info, id: str, status: bool) -> dict:
	return { '__typename': 'BugReport', **set_bug_status(id, status) }

@perms.module('bugs')
@perms.require('edit')
@handle_client_exceptions
def resolve_comment_on_bug(_, info, id: str, text: str, plaintext: bool) -> dict:
	return { '__typename': 'BugReport', **comment_on_bug(id, text, plaintext) }
