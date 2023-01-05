import application.exceptions as exceptions
from application.db.bugs import report_bug, delete_bug_report, get_bug_report
import application.db.perms as perms

def resolve_report_bug(_, info, title: str, text: str) -> dict:
	try:
		return { '__typename': 'BugReport', **report_bug(title, text) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_delete_bug(_, info, id: str) -> dict:
	try:
		bug_report = get_bug_report(id)
		user_data = perms.caller_info(info)

		if user_data is None:
			return perms.bad_perms()

		# Make sure user is either an admin,
		# or are trying to delete their own bug report.
		if (bug_report.get('creator') != user_data.get('username')) and not perms.user_has_perms(user_data, ['admin']):
			return perms.bad_perms()

		return { '__typename': 'BugReport', **delete_bug_report(id) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
