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
	"""
	Returns a list of user ObjectIds based on the provided username or the caller's group memberships.

	If a username is provided, returns a list containing the ObjectId of that user.
	If no username is provided, retrieves the caller's user data, extracts their groups,
		and returns ObjectIds of users in those groups.

	Args:
		username (str | None): The username to look up. If None, uses the caller's information.

	Returns:
		list[ObjectId]: A list of ObjectIds for the user(s) found.
	"""
	if username is not None:
		return [get_user_data(username)['_id']]

	user_data = perms.caller_info_strict()
	groups = user_data.get('groups', [])
	return userids_in_groups(groups)


@query.field('getBugReports')
@perms.module('bugs')
def resolve_get_bug_reports(
	_,
	_info: GraphQLResolveInfo,
	username: str | None,
	start: int,
	count: int,
	resolved: bool
) -> list[dict]:
	"""
	Fetches a list of bug reports based on the specified filters.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str | None): Username to filter bug reports by user group.
			If None, no user filtering is applied.
		start (int): The starting index for pagination.
		count (int): The number of bug reports to retrieve.
		resolved (bool): Whether to filter for resolved (True) or unresolved (False) bug reports.

	Returns:
		list[dict]: A list of dictionaries, each representing a bug report.
	"""
	return get_bug_reports(
		userids=users_in_group(username),
		start=start,
		count=count,
		resolved=resolved,
	)


@query.field('countBugReports')
@perms.module('bugs')
def resolve_count_bug_reports(
	_,
	_info: GraphQLResolveInfo,
	username: str | None,
	resolved: bool
) -> int:
	"""
	Resolves the count of bug reports for a given user or group, filtered by resolution status.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str | None): The username to filter bug reports by.
			If None, considers all users in the caller's group.
		resolved (bool): If True, counts only resolved bug reports; if False, counts unresolved ones.

	Returns:
		int: The number of bug reports matching the specified criteria.
	"""
	return count_bug_reports(users_in_group(username), resolved)


@query.field('getBugReport')
@perms.module('bugs')
def resolve_get_bug_report(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Resolves a query to retrieve a bug report by its unique identifier.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the bug report to retrieve.

	Returns:
		dict: The bug report data corresponding to the given id.
	"""
	return get_bug_report(id)


@query.field('getOpenIssues')
@perms.module('bugs')
def resolve_get_issues(_, _info: GraphQLResolveInfo) -> dict:
	"""
	Resolves and returns a list of issues for the current GitHub repository.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict: A dictionary with either:
			- '__typename': 'IssueList' and 'issues': list of issues if successful.
			- '__typename': 'RepoFetchFailed' and 'message': error message if fetching fails.
	"""
	try:
		repo = github.CurrentRepository()
		return {'__typename': 'IssueList', 'issues': repo.issues()}
	except github.RepoFetchFailed as e:
		return {'__typename': 'RepoFetchFailed', 'message': str(e)}


@query.field('getPendingIssues')
@perms.module('bugs')
def resolve_get_pending_issues(_, _info: GraphQLResolveInfo) -> dict:
	"""
	Resolves and returns a list of pending issues for the current GitHub repository.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict: A dictionary with either:
			- '__typename': 'IssueList' and 'issues': list of pending issues if successful.
			- '__typename': 'RepoFetchFailed' and 'message': error message if repository fetch fails.
	"""
	try:
		repo = github.CurrentRepository()
		return {'__typename': 'IssueList', 'issues': repo.issues_pending_resolution()}
	except github.RepoFetchFailed as e:
		return {'__typename': 'RepoFetchFailed', 'message': str(e)}
