import application.exceptions as exceptions
from application.db.blob import delete_blob, get_blob_data, set_blob_tags, zip_matching_blobs, create_blob, set_blob_hidden, BlobStorage
import application.db.perms as perms
from application.db.users import userids_in_groups
from application.objects import BlobSearchFilter
from application.tags.exceptions import ParseError
from application.integrations import qrcode

def group_filter(filter: dict, user_data: dict) -> dict:
	if filter.get('creator') is None:
		groups = user_data.get('groups', [])
		if len(groups):
			filter['creator'] = userids_in_groups(groups)

	return filter

def resolve_delete_blob(_, info, id: str) -> dict:
	try:
		blob_data = get_blob_data(id)

		# Make sure user is either an admin,
		# or are trying to delete their own blob.
		if not perms.satisfies(info, ['admin'], blob_data):
			return perms.bad_perms()

		blob_data = delete_blob(id)
		blob_data['id'] = blob_data['_id']
		return { '__typename': 'Blob', **blob_data }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_set_blob_tags(_, info, id: str, tags: list) -> dict:
	try:
		return { '__typename': 'Blob', **set_blob_tags(id, tags) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_create_zip_archive(_, info, filter: BlobSearchFilter) -> dict:
	try:
		user_data = perms.caller_info(info)
		blob = zip_matching_blobs(group_filter(filter, user_data), user_data['_id'])
		return { '__typename': 'Blob', **blob }
	except ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_generate_blob_from_qr(_, info, text: str|None) -> dict:
	try:
		id, ext = create_blob('QR.png', tags = ['qr', '__temp_file'])
		qrcode.generate(BlobStorage(id, ext).path(create = True), text if text is not None else id)
		return { '__typename': 'Blob', **get_blob_data(id) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'])
def resolve_set_blob_hidden(_, info, id: str, hidden: bool) -> dict:
	try:
		return { '__typename': 'Blob', **set_blob_hidden(id, hidden) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
