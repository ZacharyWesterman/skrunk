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
		id (str): The ID of the inventory item.
		rfid (str | None): The new RFID tag to link to the item, or None to unlink.

	Returns:
		dict: The updated inventory item with the new RFID tag.
	"""
	return {'__typename': 'Item', **relink_inventory_item(id, rfid)}
