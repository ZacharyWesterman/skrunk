from application.db.bugs import report_bug

def resolve_report_bug(_, info, title: str, text: str) -> bool:
	return report_bug(title, text)
