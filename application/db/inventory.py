from application.tokens import decode_user_token, get_request_token
from . import users
from datetime import datetime
import markdown
from application.objects import InventorySearchFilter, Sorting
from bson.objectid import ObjectId
import application.exceptions as exceptions
from . import blob

db = None

def create_inventory_item(category: str, type: str, location: str, blob_id: str, description: str) -> dict:
	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	item = {
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'category': category.strip(),
		'type': type.strip(),
		'location': location.strip(),
		'blob': ObjectId(blob_id),
		'description': description,
		'description_html': markdown.markdown(description, output_format = 'html'),
	}

	db.items.insert_one(item)

	return item

def get_item_categories() -> list[str]:
	return [ i for i in db.items.distinct('category') ]

def get_item_types(category: str) -> list[str]:
	return [ i for i in db.items.distinct('type', {'category': category}) ]

def get_item_locations(owner: str) -> list[str]:
	user_data = users.get_user_data(owner)
	return [ i for i in db.items.distinct('location', {'creator': user_data['_id']}) ]

def build_inventory_query(filter: InventorySearchFilter, user_id: ObjectId) -> dict:
	query = [{}]

	creator = filter.get('owner')
	if type(creator) is str:
		user_data= users.get_user_data(creator)
		query += [{'creator': user_data['_id']}]

	if type(creator) is list and len(creator):
		query += [{'$or': [{'creator': i} for i in creator]}]

	if filter.get('category') is not None:
		query += [{'category': filter.get('category')}]

	if filter.get('type') is not None:
		query += [{'type': filter.get('type')}]

	if filter.get('location') is not None:
		query += [{'location': filter.get('location')}]

	return {'$and': query} if len(query) else {}

def get_inventory(filter: InventorySearchFilter, start: int, count: int, sorting: Sorting, user_id: ObjectId) -> list:
	try:
		query = build_inventory_query(filter, user_id)
	except exceptions.UserDoesNotExistError:
		return []

	items = []

	if 'created' not in sorting['fields']:
		sorting['fields'] += ['created']

	sort = [(i, -1 if sorting['descending'] else 1) for i in sorting['fields']]

	selection = db.items.find(query, sort = sort)
	for i in selection.limit(count).skip(start):
		try:
			i['creator'] = users.get_user_by_id(i['creator'])
		except exceptions.UserDoesNotExistError:
			i['creator'] = {
				'username': i['creator'],
				'display_name': i['creator'],
			}

		i['id'] = i['_id']
		i['blob'] = blob.get_blob_data(i['blob'])
		if i['blob'] is None:
			i['blob'] = {
				'thumbnail': 'DELETED',
			}
		items += [i]

	return items

def count_inventory(filter: InventorySearchFilter, user_id: ObjectId) -> list:
	try:
		query = build_inventory_query(filter, user_id)
	except exceptions.UserDoesNotExistError:
		return 0

	print(query, flush=True)

	return db.items.count_documents(query)
