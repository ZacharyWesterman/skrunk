from application.db.blob import *
from application.tags import exceptions
from application.objects import BlobSearchFilter, Sorting
import application.db.perms as perms
from application.db.users import group_filter, userids_in_groups
from application.integrations import qrcode
from ..decorators import *
from . import query

@query.field('getBlobs')
@perms.module('files')
def resolve_get_blobs(_, info, filter: BlobSearchFilter, start: int, count: int, sorting: Sorting) -> dict:
	try:
		user_data = perms.caller_info()
		blobs = get_blobs(group_filter(filter, user_data), start, count, sorting, user_data['_id'])
		return { '__typename': 'BlobList', 'blobs': blobs }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

@query.field('countBlobs')
@perms.module('files')
def resolve_count_blobs(_, info, filter: BlobSearchFilter) -> dict:
	try:
		user_data = perms.caller_info()
		count = count_blobs(group_filter(filter, user_data), user_data['_id'])
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

@query.field('getBlob')
@perms.module('files')
@handle_client_exceptions
def resolve_get_blob(_, info, id: str) -> dict:
	return get_blob_data(id)

@query.field('totalBlobSize')
@perms.module('files')
def resolve_total_blob_size(_, info, filter: BlobSearchFilter) -> dict:
	try:
		user_data = perms.caller_info()
		count = sum_blob_size(group_filter(filter, user_data), user_data['_id'])
		return { '__typename': 'BlobCount', 'count': count }
	except exceptions.ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }

@query.field('getQRFromBlob')
@perms.module('files')
def resolve_process_qr_from_blob(_, info, id: str) -> str|None:
	try:
		blob_data = get_blob_data(id)
		file_path = BlobStorage(id, blob_data['ext']).path()
		return qrcode.process(file_path)
	except Exception as e:
		print(e, flush=True)
		return None

@query.field('countTagUses')
@perms.module('files')
def resolve_count_tag_uses(_, info, tag: str) -> int:
	group = userids_in_groups(perms.caller_info().get('groups', []))
	return count_tag_uses(tag, group)

@query.field('generateUID')
def resolve_generate_uid(_, info) -> str:
	return get_uid()

@query.field('pollZipProgress')
@perms.module('files')
@handle_client_exceptions
def resolve_poll_zip_progress(_, info, uid: str) -> dict:
	return { '__typename': 'ZipProgress', **get_zip_progress(uid) }
