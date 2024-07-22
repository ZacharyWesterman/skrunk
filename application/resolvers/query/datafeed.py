from application.db.datafeed import get_user_feeds
from application.exceptions import ClientError

def resolve_get_user_feeds(_, info, username: str) -> list[dict]:
	try:
		return get_user_feeds(username)
	except ClientError:
		return []
