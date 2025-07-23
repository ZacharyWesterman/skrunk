"""application.resolvers.query.blob"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.blob import (count_blobs, count_tag_uses, get_blob_data,
                                 get_blobs, get_uid, get_zip_progress,
                                 sum_blob_size)
from application.db.users import group_filter, userids_in_groups
from application.integrations import qrcode
from application.tags import exceptions
from application.types import BlobSearchFilter, Sorting, UserData
from application.types.blob_storage import BlobStorage

from ..decorators import handle_client_exceptions
from . import query


@query.field('getBlobs')
@perms.module('files')
def resolve_get_blobs(
	_,
	_info: GraphQLResolveInfo,
	filter: BlobSearchFilter,
	start: int,
	count: int,
	sorting: Sorting
) -> dict:
	"""
	Resolves the retrieval of blobs based on provided filters, pagination, and sorting options.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (BlobSearchFilter): Filter criteria for searching blobs.
		start (int): The starting index for pagination.
		count (int): The number of blobs to retrieve.
		sorting (Sorting): Sorting options for the blob list.

	Returns:
		dict: A dictionary representing a BlobList if successful, or a BadTagQuery if a ParseError occurs.

	Raises:
		None: All exceptions are handled internally and returned as part of the response.
	"""
	try:
		user_data = perms.caller_info_strict()
		blobs = get_blobs(
			group_filter(filter, user_data),  # type: ignore[assignment]
			start,
			count,
			sorting,
			user_data['_id']
		)
		return {'__typename': 'BlobList', 'blobs': blobs}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}


@query.field('countBlobs')
@perms.module('files')
def resolve_count_blobs(_, _info: GraphQLResolveInfo, filter: BlobSearchFilter) -> dict:
	"""
	Resolves the count of blobs matching the provided filter.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (BlobSearchFilter): Filter criteria for searching blobs.

	Returns:
		dict: A dictionary representing a BlobCount if successful,
			or a BadTagQuery if a ParseError occurs.

	Raises:
		None: All exceptions are handled internally and returned as part of the response.
	"""
	try:
		user_data: UserData = perms.caller_info_strict()  # type: ignore[assignment]
		count = count_blobs(group_filter(filter, user_data), user_data['_id'])  # type: ignore[assignment]
		return {'__typename': 'BlobCount', 'count': count}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}


@query.field('getBlob')
@perms.module('files')
@handle_client_exceptions
def resolve_get_blob(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Resolves the retrieval of blob data by its unique identifier.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the blob to retrieve.

	Returns:
		dict: The data associated with the specified blob.
	"""
	return get_blob_data(id)


@query.field('totalBlobSize')
@perms.module('files')
def resolve_total_blob_size(_, _info: GraphQLResolveInfo, filter: BlobSearchFilter) -> dict:
	"""
	Resolves the total size of blobs matching the given filter.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (BlobSearchFilter): Filter criteria for searching blobs.

	Returns:
		dict: A dictionary representing the total size of all blobs matching the filter,
			or a BadTagQuery if a ParseError occurs.

	Raises:
		None: All exceptions are handled internally and returned as part of the response.
	"""
	try:
		user_data = perms.caller_info_strict()
		count = sum_blob_size(
			group_filter(filter, user_data),  # type: ignore[assignment]
			user_data['_id']
		)
		return {'__typename': 'BlobCount', 'count': count}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}


@query.field('getQRFromBlob')
@perms.module('files')
def resolve_process_qr_from_blob(_, _info: GraphQLResolveInfo, id: str) -> dict | None:
	"""
	Resolves a query to process a QR code from a blob storage.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The identifier of the blob to process.

	Returns:
		dict | None: The result of the QR code processing as a dictionary, or None if an error occurs.
	"""
	# pylint: disable=broad-except
	try:
		blob_data = get_blob_data(id)
		file_path = BlobStorage(id, blob_data['ext']).path()
		return qrcode.process(file_path)
	except Exception as e:
		print(e, flush=True)
		return None
	# pylint: enable=broad-except


@query.field('countTagUses')
@perms.module('files')
def resolve_count_tag_uses(_, _info: GraphQLResolveInfo, tag: str) -> int:
	"""
	Resolves the number of times a specific tag has been used by users in the caller's groups.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		tag (str): The tag to count usages for.

	Returns:
		int: The number of times the specified tag has been used by users in the caller's groups.
	"""
	group = userids_in_groups(perms.caller_info_strict().get('groups', []))
	return count_tag_uses(tag, group)


@query.field('generateUID')
def resolve_generate_uid(_, _info: GraphQLResolveInfo) -> str:
	"""
	Resolves the GraphQL query for generating a unique identifier (UID).

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		str: A newly generated unique identifier.
	"""
	return get_uid()


@query.field('pollZipProgress')
@perms.module('files')
@handle_client_exceptions
def resolve_poll_zip_progress(_, _info: GraphQLResolveInfo, uid: str) -> dict:
	"""
	Resolves the current progress of a zip operation identified by the given UID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		uid (str): Unique identifier for the zip operation whose progress is being queried.

	Returns:
		dict: A dictionary representing the progress of the zip operation.
	"""
	return {'__typename': 'ZipProgress', **get_zip_progress(uid)}
