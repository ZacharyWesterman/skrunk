from application.db.bugs import *
from application.integrations import github

def resolve_get_bug_reports(_, info, username: str|None, start: int, count: int, resolved: bool) -> dict:
	return get_bug_reports(
		username = username,
		start = start,
		count = count,
		resolved = resolved,
	)

def resolve_count_bug_reports(_, info, username: str|None, resolved: bool) -> dict:
	return count_bug_reports(username, resolved)

def resolve_get_bug_report(_, info, id: str) -> dict:
	return get_bug_report(id)

def resolve_get_issues(_, info) -> list:
	repo = github.CurrentRepository()
	return repo.issues()
