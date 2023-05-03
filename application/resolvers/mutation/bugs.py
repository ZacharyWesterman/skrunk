import application.exceptions as exceptions
from application.db.bugs import *
import application.db.perms as perms

def resolve_report_bug(_, info, title: str, text: str) -> dict:
	try:
		return { '__typename': 'BugReport', **report_bug(title, text) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_delete_bug(_, info, id: str) -> dict:
	try:
		bug_report = get_bug_report(id)

		# Make sure user is either an admin,
		# or are trying to delete their own bug report.
		if not perms.satisfies(info, ['admin'], bug_report):
			return perms.bad_perms()

		return { '__typename': 'BugReport', **delete_bug_report(id) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'])
def resolve_set_bug_status(_, info, id: str, status: bool) -> dict:
	try:
		return { '__typename': 'BugReport', **set_bug_status(id, status) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }