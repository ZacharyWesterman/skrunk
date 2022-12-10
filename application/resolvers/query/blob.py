from application.db.blob import get_user_blobs, count_user_blobs

def resolve_get_user_blobs(_, info, username: str, start: int, count: int) -> list:
	return get_user_blobs(username, start, count)

def resolve_count_user_blobs(_, info, username: str) -> int:
	return count_user_blobs(username)
