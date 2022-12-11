import application.exceptions as exceptions
from application.db.blob import delete_blob
import application.db.perms as perms

@perms.require(['admin'])
def resolve_delete_blob(_, info, id: str) -> dict:
	try:
		blob_data = delete_blob(id)
		blob_data['id'] = blob_data['_id']
		return { '__typename': 'Blob', **blob_data }
	except exceptions.ClientError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }
