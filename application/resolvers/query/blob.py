from typing import Optional
from application.db.blob import *
from application.tags import exceptions
from ariadne import convert_kwargs_to_snake_case

@convert_kwargs_to_snake_case
def resolve_get_blobs(_, info, username: Optional[str], start: int, count: int, tags: Optional[str], begin_date: Optional[datetime], end_date: Optional[datetime], name: Optional[str]) -> dict:
	try:
		blobs = get_blobs(
			username = username,
			start = start,
			count = count,
			tagstr = tags,
			begin_date = begin_date,
			end_date = end_date,
			name = name,
		)
		return { '__typename': 'BlobList', 'blobs': blobs }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

@convert_kwargs_to_snake_case
def resolve_count_blobs(_, info, username: Optional[str], tags: Optional[str], begin_date: Optional[datetime], end_date: Optional[datetime], name: Optional[str]) -> dict:
	try:
		count = count_blobs(
			username = username,
			tagstr = tags,
			begin_date = begin_date,
			end_date = end_date,
			name = name,
		)
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_get_blob(_, info, id: str) -> dict:
	return get_blob_data(id)
