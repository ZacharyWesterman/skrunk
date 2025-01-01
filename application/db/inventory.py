from application.tokens import decode_user_token, get_request_token
from . import users
from datetime import datetime
import markdown
from application.objects import InventorySearchFilter, Sorting
from bson.objectid import ObjectId
import application.exceptions as exceptions
from . import blob

from pymongo.database import Database
db: Database = None


def create_inventory_item(owner: str, category: str, type: str, location: str, blob_id: str, description: str, rfid: str | None) -> dict:
	"""
	Create a new inventory item in the database.

	Args:
		owner (str): The username of the owner of the item.
		category (str): The category of the item.
		type (str): The type of the item.
		location (str): The location of the item.
		blob_id (str): The ID of the associated blob.
		description (str): A textual description of the item.
		rfid (str | None): The RFID tag of the item, if any.

	Returns:
		dict: The created inventory item.

	Raises:
		exceptions.ItemExistsError: If an item with the given RFID already exists.
	"""
	owner_data = users.get_user_data(owner)

	if db.items.find_one({'rfid': rfid}):
		raise exceptions.ItemExistsError(rfid)

	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	item = {
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'owner': owner_data['_id'],
		'category': category.strip(),
		'type': type.strip(),
		'location': location.strip(),
		'blob': ObjectId(blob_id),
		'description': description,
		'description_html': markdown.markdown(description, output_format='html'),
		'rfid': [] if rfid is None else [rfid],
	}

	db.items.insert_one(item)
	blob.add_reference(blob_id)

	return item


def get_inventory_item(id: str) -> dict:
	"""
	Retrieve an inventory item from the database by its ID.

	Args:
		id (str): The ID of the inventory item to retrieve.

	Returns:
		dict: A dictionary representing the inventory item.

	Raises:
		exceptions.ItemDoesNotExistError: If no item with the given ID is found.
	"""
	item = db.items.find_one({'_id': ObjectId(id)})
	if item is None:
		raise exceptions.ItemDoesNotExistError(id)

	item['id'] = item['_id']
	return item


def delete_inventory_item(id: str) -> dict:
	"""
	Deletes an inventory item from the database by its ID.

	Args:
		id (str): The ID of the inventory item to be deleted.

	Returns:
		dict: The deleted inventory item details.

	Raises:
		ValueError: If the inventory item with the given ID does not exist.
	"""
	item = get_inventory_item(id)
	db.items.delete_one({'_id': ObjectId(id)})
	if blob_id := item.get('blob'):
		blob.remove_reference(str(blob_id))

	return item


def get_item_categories() -> list[str]:
	"""
	Retrieve a list of distinct item categories from the database.

	Returns:
		list[str]: A list of unique item categories.
	"""
	return [i for i in db.items.distinct('category')]


def get_item_types(category: str) -> list[str]:
	"""
	Retrieve a list of distinct item types for a given category from the database.

	Args:
		category (str): The category of items to filter by.

	Returns:
		list[str]: A list of distinct item types within the specified category.
	"""
	return [i for i in db.items.distinct('type', {'category': category})]


def get_item_locations(owner: str) -> list[str]:
	"""
	Retrieve a list of distinct item locations for a given owner.

	Args:
		owner (str): The username of the owner whose item locations are to be retrieved.

	Returns:
		list[str]: A list of distinct locations where the owner's items are stored.
	"""
	user_data = users.get_user_data(owner)
	return [i for i in db.items.distinct('location', {'creator': user_data['_id']})]


def build_inventory_query(filter: InventorySearchFilter, user_id: ObjectId) -> dict:
	"""
	Builds a MongoDB query dictionary for searching inventory based on the provided filter and user ID.

	Args:
		filter (InventorySearchFilter): An object containing search criteria for the inventory.
		user_id (ObjectId): The ID of the user making the query.

	Returns:
		dict: A MongoDB query dictionary constructed based on the provided filter criteria.
	"""
	query = [{}]

	owner = filter.get('owner')
	if type(owner) is str:
		user_data = users.get_user_data(owner)
		query += [{'owner': user_data['_id']}]

	if type(owner) is list and len(owner):
		query += [{'$or': [{'owner': i} for i in owner]}]

	if filter.get('category') is not None:
		query += [{'category': filter.get('category')}]

	if filter.get('type') is not None:
		query += [{'type': filter.get('type')}]

	if filter.get('location') is not None:
		query += [{'location': filter.get('location')}]

	return {'$and': query} if len(query) else {}


def get_inventory(filter: InventorySearchFilter, start: int, count: int, sorting: Sorting, user_id: ObjectId) -> list:
	"""
	Retrieves a list of inventory items based on the provided filter, pagination, and sorting options.

	Args:
		filter (InventorySearchFilter): The filter criteria to apply to the inventory search.
		start (int): The starting index for pagination.
		count (int): The number of items to retrieve.
		sorting (Sorting): The sorting criteria for the inventory items.
		user_id (ObjectId): The ID of the user making the request.

	Returns:
		list: A list of inventory items matching the search criteria.

	Raises:
		exceptions.UserDoesNotExistError: If the user specified in the filter does not exist.
	"""
	try:
		query = build_inventory_query(filter, user_id)
	except exceptions.UserDoesNotExistError:
		return []

	items = []

	if 'created' not in sorting['fields']:
		sorting['fields'] += ['created']

	sort = [(i, -1 if sorting['descending'] else 1) for i in sorting['fields']]

	selection = db.items.find(query, sort=sort)
	for i in selection.limit(count).skip(start):
		try:
			i['creator'] = users.get_user_by_id(i['creator'])
		except exceptions.UserDoesNotExistError:
			i['creator'] = {
				'username': i['creator'],
				'display_name': i['creator'],
			}

		try:
			i['owner'] = users.get_user_by_id(i['owner'])
		except exceptions.UserDoesNotExistError:
			i['owner'] = {
				'username': i['owner'],
				'display_name': i['owner'],
			}

		i['id'] = i['_id']
		blob_id = str(i['blob'])
		i['blob'] = blob.get_blob_data(i['blob'])
		if i['blob'] is None:
			i['blob'] = {
				'thumbnail': 'DELETED',
				'id': blob_id,
				'ext': '',
			}
		items += [i]

	return items


def count_inventory(filter: InventorySearchFilter, user_id: ObjectId) -> list:
	"""
	Count the number of inventory items based on the provided filter and user ID.

	Args:
		filter (InventorySearchFilter): The filter criteria to apply to the inventory search.
		user_id (ObjectId): The ID of the user whose inventory is being queried.

	Returns:
		int: The number of inventory items that match the filter criteria for the specified user.
			 Returns 0 if the user does not exist.

	Raises:
		exceptions.UserDoesNotExistError: If the user does not exist.
	"""
	try:
		query = build_inventory_query(filter, user_id)
	except exceptions.UserDoesNotExistError:
		return 0

	return db.items.count_documents(query)
