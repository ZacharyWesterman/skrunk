from application.db.blob import *

def resolve_get_user_blobs(_, info, username: str, start: int, count: int) -> list:
	return get_user_blobs(username, start, count)

def resolve_count_user_blobs(_, info, username: str) -> int:
	return count_user_blobs(username)

def resolve_count_all_blobs(_, info) -> int:
	return count_all_blobs()

def resolve_get_all_blobs(_, info, start: int, count: int) -> list:
	return get_all_blobs(start, count)

def resolve_get_blob(_, info, id: str) -> dict:
	return get_blob_data(id)
