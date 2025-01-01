"""application.resolvers.query.bugs"""

from application.db.bugs import *
from application.integrations import github
import application.db.perms as perms
from application.db.users import userids_in_groups, get_user_data
from . import query


def users_in_group(info, username: str | None) -> dict:
	if username is not None:
		return [get_user_data(username)['_id']]

	user_data = perms.caller_info()
	groups = user_data.get('groups', [])
	return userids_in_groups(groups)


@query.field('getBugReports')
@perms.module('bugs')
def resolve_get_bug_reports(_, info, username: str | None, start: int, count: int, resolved: bool) -> dict:
	return get_bug_reports(
		userids=users_in_group(info, username),
		start=start,
		count=count,
		resolved=resolved,
	)


@query.field('countBugReports')
@perms.module('bugs')
def resolve_count_bug_reports(_, info, username: str | None, resolved: bool) -> dict:
	return count_bug_reports(users_in_group(info, username), resolved)


@query.field('getBugReport')
@perms.module('bugs')
def resolve_get_bug_report(_, info, id: str) -> dict:
	return get_bug_report(id)


@query.field('getOpenIssues')
@perms.module('bugs')
def resolve_get_issues(_, info) -> list:
	try:
		repo = github.CurrentRepository()
		return {'__typename': 'IssueList', 'issues': repo.issues()}
	except github.RepoFetchFailed as e:
		return {'__typename': 'RepoFetchFailed', 'message': str(e)}


@query.field('getPendingIssues')
@perms.module('bugs')
def resolve_get_pending_issues(_, info) -> dict:
	try:
		repo = github.CurrentRepository()
		return {'__typename': 'IssueList', 'issues': repo.issues_pending_resolution()}
	except github.RepoFetchFailed as e:
		return {'__typename': 'RepoFetchFailed', 'message': str(e)}
