
import application.exceptions as exceptions
import application.db.perms as perms
from application.db.inventory import create_inventory_item

@perms.require(['edit'])
def resolve_create_inventory_item(_, info, owner: str, category: str, type: str, location: str, blob_id: str, description: str, rfid: str|None) -> dict:
	if category.strip() == '' or type.strip() == '' or location.strip() == '' or blob_id.strip() == '':
		fields = []
		if category.strip() == '': fields += ['category']
		if type.strip() == '': fields += ['type']
		if location.strip() == '': fields += ['location']
		if blob_id.strip() == '': fields += ['blob_id']

		return {
			'__typename': 'InvalidFields',
			'message': f'The following field{"" if len(fields) == 1 else "s"} cannot be blank',
			'fields': fields,
		}

	try:
		return { '__typename': 'Item', **create_inventory_item(owner, category, type, location, blob_id, description, rfid) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
