"""application.resolvers.mutation.blob"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.blob import (BlobStorage, cancel_zip, create_blob,
                                 delete_blob, get_blob_data,
                                 set_blob_ephemeral, set_blob_hidden,
                                 set_blob_tags, zip_matching_blobs)
from application.db.users import group_filter
from application.integrations import qrcode
from application.tags import exceptions
from application.types import BlobSearchFilter

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('deleteBlob')
@perms.module('files')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_blob_data)
@handle_client_exceptions
def resolve_delete_blob(_, _info: GraphQLResolveInfo, id: str) -> dict:
	blob_data = get_blob_data(id)

	blob_data = delete_blob(id)
	blob_data['id'] = blob_data['_id']
	return {'__typename': 'Blob', **blob_data}


@mutation.field('setBlobTags')
@perms.module('files')
@perms.require('edit')
@handle_client_exceptions
def resolve_set_blob_tags(_, _info: GraphQLResolveInfo, id: str, tags: list) -> dict:
	return {'__typename': 'Blob', **set_blob_tags(id, tags)}


@mutation.field('createZipArchive')
@perms.module('files')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_zip_archive(_, _info: GraphQLResolveInfo, filter: BlobSearchFilter, uid: str) -> dict:
	try:
		user_data = perms.caller_info_strict()
		groups: BlobSearchFilter = group_filter(filter, user_data)  # type: ignore
		blob = zip_matching_blobs(groups, user_data['_id'], uid)
		return {'__typename': 'Blob', **blob}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}


@mutation.field('getBlobFromQR')
@perms.module('files')
@perms.require('edit')
@handle_client_exceptions
def resolve_generate_blob_from_qr(_, _info: GraphQLResolveInfo, text: str | None, amount: int) -> dict:
	amount = min(70, max(1, amount))
	id, ext = create_blob('QR.png', tags=['qr', '__temp_file'], ephemeral=True)
	qrcode.generate(BlobStorage(id, ext).path(create=True), text, amount)
	return {'__typename': 'Blob', **get_blob_data(id)}


@mutation.field('setBlobHidden')
@perms.module('files')
@perms.require('edit')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_blob_hidden(_, _info: GraphQLResolveInfo, id: str, hidden: bool) -> dict:
	return {'__typename': 'Blob', **set_blob_hidden(id, hidden)}


@mutation.field('setBlobEphemeral')
@perms.module('files')
@perms.require('edit')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_blob_ephemeral(_, _info: GraphQLResolveInfo, id: str, ephemeral: bool) -> dict:
	return {'__typename': 'Blob', **set_blob_ephemeral(id, ephemeral)}


@mutation.field('cancelZipArchive')
@perms.module('files')
@perms.require('edit')
def resolve_cancel_zip_archive(_, _info: GraphQLResolveInfo, uid: str) -> dict:
	return {'__typename': 'ZipProgress', **cancel_zip(uid)}
