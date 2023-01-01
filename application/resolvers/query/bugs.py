from typing import Optional
from application.db.bugs import *

def resolve_get_bug_reports(_, info, username: Optional[str], start: int, count: int, resolved: bool) -> dict:
	return get_bug_reports(
		username = username,
		start = start,
		count = count,
		resolved = resolved,
	)

def resolve_count_bug_reports(_, info, username: Optional[str], resolved: bool) -> dict:
	return count_bug_reports(username, resolved)

def resolve_get_bug_report(_, info, id: str) -> dict:
	return get_bug_report(id)