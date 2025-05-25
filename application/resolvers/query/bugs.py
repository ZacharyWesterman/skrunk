"""application.resolvers.query.bugs"""

from bson.objectid import ObjectId
from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.bugs import (count_bug_reports, get_bug_report,
                                 get_bug_reports)
from application.db.users import get_user_data, userids_in_groups
from application.integrations import github

from . import query


def users_in_group(username: str | None) -> list[ObjectId]:
	if username is not None:
		return [get_user_data(username)['_id']]

	user_data = perms.caller_info_strict()
	groups = user_data.get('groups', [])
	return userids_in_groups(groups)


@query.field('getBugReports')
@perms.module('bugs')
def resolve_get_bug_reports(_, _info: GraphQLResolveInfo, username: str | None, start: int, count: int, resolved: bool) -> list[dict]:
	return get_bug_reports(
		userids=users_in_group(username),
		start=start,
		count=count,
		resolved=resolved,
	)


@query.field('countBugReports')
@perms.module('bugs')
def resolve_count_bug_reports(_, _info: GraphQLResolveInfo, username: str | None, resolved: bool) -> int:
	return count_bug_reports(users_in_group(username), resolved)


@query.field('getBugReport')
@perms.module('bugs')
def resolve_get_bug_report(_, _info: GraphQLResolveInfo, id: str) -> dict:
	return get_bug_report(id)


@query.field('getOpenIssues')
@perms.module('bugs')
def resolve_get_issues(_, _info: GraphQLResolveInfo) -> dict:
	try:
		repo = github.CurrentRepository()
		return {'__typename': 'IssueList', 'issues': repo.issues()}
	except github.RepoFetchFailed as e:
		return {'__typename': 'RepoFetchFailed', 'message': str(e)}


@query.field('getPendingIssues')
@perms.module('bugs')
def resolve_get_pending_issues(_, _info: GraphQLResolveInfo) -> dict:
	try:
		repo = github.CurrentRepository()
		return {'__typename': 'IssueList', 'issues': repo.issues_pending_resolution()}
	except github.RepoFetchFailed as e:
		return {'__typename': 'RepoFetchFailed', 'message': str(e)}
