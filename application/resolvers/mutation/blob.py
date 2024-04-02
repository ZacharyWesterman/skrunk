import application.exceptions as exceptions
from application.db.blob import delete_blob, get_blob_data, set_blob_tags, zip_matching_blobs, create_blob, set_blob_hidden, BlobStorage, set_blob_ephemeral
import application.db.perms as perms
from application.db.users import group_filter
from application.objects import BlobSearchFilter
from application.tags.exceptions import ParseError
from application.integrations import qrcode

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True, data_func = get_blob_data)
def resolve_delete_blob(_, info, id: str) -> dict:
	try:
		blob_data = get_blob_data(id)

		blob_data = delete_blob(id)
		blob_data['id'] = blob_data['_id']
		return { '__typename': 'Blob', **blob_data }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_set_blob_tags(_, info, id: str, tags: list) -> dict:
	try:
		return { '__typename': 'Blob', **set_blob_tags(id, tags) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_create_zip_archive(_, info, filter: BlobSearchFilter) -> dict:
	try:
		user_data = perms.caller_info()
		blob = zip_matching_blobs(group_filter(filter, user_data), user_data['_id'])
		return { '__typename': 'Blob', **blob }
	except ParseError as e:
		return { '__typename': 'BadTagQuery', 'message': str(e) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
def resolve_generate_blob_from_qr(_, info, text: str|None, amount: int) -> dict:
	try:
		amount = min(70, max(1, amount))
		id, ext = create_blob('QR.png', tags = ['qr', '__temp_file'], ephemeral = True)
		qrcode.generate(BlobStorage(id, ext).path(create = True), text, amount)
		return { '__typename': 'Blob', **get_blob_data(id) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True)
def resolve_set_blob_hidden(_, info, id: str, hidden: bool) -> dict:
	try:
		return { '__typename': 'Blob', **set_blob_hidden(id, hidden) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['edit'])
@perms.require(['admin'], perform_on_self = True)
def resolve_set_blob_ephemeral(_, info, id: str, ephemeral: bool) -> dict:
	try:
		return { '__typename': 'Blob', **set_blob_ephemeral(id, ephemeral) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
