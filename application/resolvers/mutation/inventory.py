"""application.resolvers.mutation.inventory"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.inventory import (create_inventory_item,
                                      delete_inventory_item,
                                      get_inventory_item,
                                      relink_inventory_item)

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('createInventoryItem')
@perms.module('inventory')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_inventory_item(
	_,
    _info: GraphQLResolveInfo,
    owner: str,
    category: str,
    type: str,
    location: str,
    blob_id: str,
    description: str,
    rfid: str | None
) -> dict:
	"""
	Create a new inventory item.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		owner (str): The username of the owner of the inventory item.
		category (str): The category of the inventory item.
		type (str): The type of the inventory item.
		location (str): The location of the inventory item.
		blob_id (str): The ID of the blob associated with the inventory item.
		description (str): A description of the inventory item.
		rfid (str | None): An RFID or QR code attached to the inventory item, if any.

	Returns:
		dict: The created inventory item, or an error message if any fields are blank.
	"""
	if category.strip() == '' or type.strip() == '' or location.strip() == '' or blob_id.strip() == '':
		fields = []
		if category.strip() == '':
			fields += ['category']
		if type.strip() == '':
			fields += ['type']
		if location.strip() == '':
			fields += ['location']
		if blob_id.strip() == '':
			fields += ['blob_id']

		return {
			'__typename': 'InvalidFields',
			'message': f'The following field{"" if len(fields) == 1 else "s"} cannot be blank',
			'fields': fields,
		}

	return {
		'__typename': 'Item',
		**create_inventory_item(owner, category, type, location, blob_id, description, rfid)
	}


@mutation.field('deleteInventoryItem')
@perms.module('inventory')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_inventory_item)
@handle_client_exceptions
def resolve_delete_inventory_item(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Deletes an inventory item by its ID and returns the result as a dictionary.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the inventory item to delete.

	Returns:
		dict: A dictionary representing the deleted item.
	"""
	return {'__typename': 'Item', **delete_inventory_item(id)}


@mutation.field('relinkInventoryItem')
@perms.module('inventory')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_inventory_item)
@handle_client_exceptions
def resolve_relink_inventory_item(_, _info: GraphQLResolveInfo, id: str, rfid: str | None) -> dict:
	"""
	Change the RFID tag of an inventory item.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The ID of the inventory item.
		rfid (str | None): The new RFID tag to link to the item, or None to unlink.

	Returns:
		dict: The updated inventory item with the new RFID tag.
	"""
	return {'__typename': 'Item', **relink_inventory_item(id, rfid)}
