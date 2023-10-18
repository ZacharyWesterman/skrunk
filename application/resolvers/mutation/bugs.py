import application.exceptions as exceptions
from application.db.bugs import *
import application.db.perms as perms

@perms.require(['edit'])
def resolve_report_bug(_, info, text: str, plaintext: bool) -> dict:
	try:
		return { '__typename': 'BugReport', **report_bug(text, plaintext) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True, data_func = get_bug_report)
def resolve_delete_bug(_, info, id: str) -> dict:
	try:
		return { '__typename': 'BugReport', **delete_bug_report(id) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True)
def resolve_set_bug_status(_, info, id: str, status: bool) -> dict:
	try:
		return { '__typename': 'BugReport', **set_bug_status(id, status) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_comment_on_bug(_, info, id: str, text: str, plaintext: bool) -> dict:
	try:
		return { '__typename': 'BugReport', **comment_on_bug(id, text, plaintext) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }