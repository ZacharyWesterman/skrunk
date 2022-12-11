import application.exceptions as exceptions
from application.db.blob import delete_blob, get_blob_data
import application.db.perms as perms

def resolve_delete_blob(_, info, id: str) -> dict:
	try:
		blob_data = get_blob_data(id)
		user_data = perms.caller_info(info)

		if user_data is None:
			return perms.bad_perms()

		# Make sure user is either an admin,
		# or are trying to delete their own blob.
		if (blob_data.get('creator') != user_data.get('username')) and not perms.user_has_perms(user_data, ['admin']):
			return perms.bad_perms()

		blob_data = delete_blob(id)
		blob_data['id'] = blob_data['_id']
		return { '__typename': 'Blob', **blob_data }
	except exceptions.ClientError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }
