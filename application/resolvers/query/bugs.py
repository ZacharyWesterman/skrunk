from application.db.bugs import *
from application.integrations import github
import application.db.perms as perms
from application.db.users import userids_in_groups, get_user_data

def users_in_group(info, username: str|None) -> dict:
	if username is not None:
		return [get_user_data(username)['_id']]

	user_data = perms.caller_info(info)
	groups = user_data.get('groups', [])
	return userids_in_groups(groups)

def resolve_get_bug_reports(_, info, username: str|None, start: int, count: int, resolved: bool) -> dict:
	return get_bug_reports(
		userids = users_in_group(info, username),
		start = start,
		count = count,
		resolved = resolved,
	)

def resolve_count_bug_reports(_, info, username: str|None, resolved: bool) -> dict:
	return count_bug_reports(users_in_group(info, username), resolved)

def resolve_get_bug_report(_, info, id: str) -> dict:
	return get_bug_report(id)

def resolve_get_issues(_, info) -> list:
	repo = github.CurrentRepository()
	return repo.issues()
