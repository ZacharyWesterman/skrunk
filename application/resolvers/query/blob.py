from application.db.blob import *
from application.tags import exceptions
from application.objects import BlobSearchFilter
import application.db.perms as perms
from application.db.users import userids_in_groups

def group_filter(info, filter: dict) -> dict:
	if filter.get('creator') is None:
		user_data = perms.caller_info(info)
		groups = user_data.get('groups', [])
		if len(groups):
			filter['creator'] = userids_in_groups(groups)

	return filter

def resolve_get_blobs(_, info, filter: BlobSearchFilter, start: int, count: int) -> dict:
	try:
		blobs = get_blobs(group_filter(info, filter), start, count)
		return { '__typename': 'BlobList', 'blobs': blobs }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_count_blobs(_, info, filter: BlobSearchFilter) -> dict:
	try:
		count = count_blobs(group_filter(info, filter))
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

def resolve_get_blob(_, info, id: str) -> dict:
	return get_blob_data(id)

def resolve_total_blob_size(_, info, filter: BlobSearchFilter) -> dict:
	try:
		count = sum_blob_size(group_filter(info, filter))
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }