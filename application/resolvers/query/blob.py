from application.db.blob import *
from application.tags import exceptions
from ariadne import convert_kwargs_to_snake_case
from application.objects import BlobSearchFilter

@convert_kwargs_to_snake_case
def resolve_get_blobs(_, info, filter: BlobSearchFilter, start: int, count: int) -> dict:
	try:
		blobs = get_blobs(filter, start, count)
		return { '__typename': 'BlobList', 'blobs': blobs }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

@convert_kwargs_to_snake_case
def resolve_count_blobs(_, info, filter: BlobSearchFilter) -> dict:
	try:
		count = count_blobs(filter)
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_get_blob(_, info, id: str) -> dict:
	return get_blob_data(id)
