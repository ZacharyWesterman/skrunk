from application.db.blob import *
from application.tags import exceptions

def resolve_get_user_blobs(_, info, username: str, start: int, count: int, tags: str) -> dict:
	try:
		blobs = get_user_blobs(username, start, count, tags)
		return { '__typename': 'BlobList', 'blobs': blobs }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_count_user_blobs(_, info, username: str, tags: str) -> dict:
	try:
		count = count_user_blobs(username, tags)
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_count_all_blobs(_, info, tags: str) -> dict:
	try:
		count = count_all_blobs(tags)
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_get_all_blobs(_, info, start: int, count: int, tags: str) -> dict:
	try:
		blobs = get_all_blobs(start, count, tags)
		return { '__typename': 'BlobList', 'blobs': blobs }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_get_blob(_, info, id: str) -> dict:
	return get_blob_data(id)
