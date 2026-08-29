"""Allows users to create, read and edit arbitrary rich text documents."""

import hashlib
import pathlib
import shutil
from datetime import UTC, datetime
from zipfile import ZIP_DEFLATED, ZipFile

import markdown
import tag_query
from bson.objectid import ObjectId
from pymongo.collection import Collection

from application.exceptions import (BlobDocumentsNotSupported,
                                    BlobDoesNotExistError,
                                    DocumentDoesNotExistError,
                                    InsufficientDiskSpace,
                                    UserDoesNotExistError)
from application.types import DocumentSearchFilter
from application.types.blob_storage import BlobStorage

from . import blob, perms, settings, users

## A pointer to the Documents collection in the database.
db: Collection = None  # type: ignore[assignment]


def parse_document(doc: dict) -> dict:
	"""
	Parses a document from the database.

	Args:
		doc (dict): The document to parse.

	Returns:
		dict: The parsed document.
	"""

	doc['id'] = str(doc['_id'])

	try:
		doc['creator'] = users.get_user_by_id(doc['creator'])
	except UserDoesNotExistError:
		doc['creator'] = {
			'username': doc['creator'],
			'display_name': doc['creator'],
		}

	if doc['updater'] is not None:
		try:
			doc['updater'] = users.get_user_by_id(doc['updater'])
		except UserDoesNotExistError:
			doc['updater'] = {
				'username': doc['updater'],
				'display_name': doc['updater'],
			}

	if doc['blob_id'] is not None:
		doc['body_html'] = ''
	else:
		doc['body_html'] = markdown.markdown(doc['body'])

	doc['shared_users'] = [
		users.get_user_by_id(i) for i in doc.get('shared_users', [])
	]

	return doc


def get_document(id: str) -> dict:
	"""
	Retrieves a document from the database by its ID.

	Args:
		id (str): The ID of the document to retrieve.

	Returns:
		dict: The document.
	"""
	if doc := db.find_one({'_id': ObjectId(id)}):
		return parse_document(doc)

	raise DocumentDoesNotExistError(id)


def build_doc_query(filter: DocumentSearchFilter | None = None) -> dict:
	"""
	Builds a MongoDB query for searching documents based on
	who created them and who they're shared with.

	Args:
		filter (DocumentSearchFilter | None): Options for filtering documents.

	Returns:
		dict: A MongoDB query dictionary.
	"""

	user_data = perms.caller_info_strict()

	query = [
		{'history': False}
	]
	query_or = [
		{'creator': user_data['_id']},
		{'shared_users': user_data['_id']},
		*[{'shared_groups': i} for i in user_data['groups']],
	]

	if filter is not None:
		title = filter.get('title')
		tag_expr = filter.get('tag_expr')

		if title is not None:
			query += [{'title': {'$regex': title, '$options': 'i'}}]

		if tag_expr is not None:
			tag_q = tag_query.compile_query(
				tag_expr,
				'tags',
				title=None
			)
			if tag_q:
				query += [tag_q]

		shared = filter.get('shared')
		if shared is True:
			query_or = [
				{'shared_users': user_data['_id']},
				*[{'shared_groups': i} for i in user_data['groups']],
			]
		elif shared is False:
			query_or = []
			query += [{'creator': user_data['_id']}]

	if query_or:
		query += [{'$or': query_or}]

	return {'$and': query}


def get_documents(filter: DocumentSearchFilter, start: int, count: int) -> list:
	"""
	Retrieves a list of documents.

	Args:
		filter (DocumentSearchFilter): Options for filtering documents.
		start (int): The starting index for pagination.
		count (int): The number of books to retrieve.

	Returns:
		list: A list of documents.
	"""

	aggregate = db.aggregate([
		{'$match': build_doc_query(filter)},
		{
			'$addFields': {
				'modified': {'$ifNull': ['$updated', '$created']},
			}
		},
		{'$sort': {'modified': -1}},
		{'$facet': {'results': [{'$skip': start}, {'$limit': count}]}},
	])

	return [parse_document(doc) for doc in next(aggregate).get('results', [])]


def count_documents(filter: DocumentSearchFilter) -> int:
	"""
	Count the total number of documents.

	Args:
		filter (DocumentSearchFilter): Options for filtering documents.

	Returns:
		int: The total number of documents.
	"""
	return db.count_documents(build_doc_query(filter))


def count_tag_uses(tag: str) -> int:
	"""
	Count the number of documents that contain a specific tag
	and are available for the current user to view.

	Args:
		tag (str): The tag to search for in the documents.

	Returns:
		int: The count of documents that match the specified tag and creators.
	"""
	query = {
		'tags': tag,
		**build_doc_query(),
	}
	return db.count_documents(query)


def create_document(title: str, body: str, is_blob: bool = False) -> dict:
	"""
	Creates a new document in the database.

	Args:
		title (str): The title of the document.
		body (str): The content of the document.
		is_blob (bool): If true, create a blank blob document.

	Returns:
		dict: The new document.
	"""

	caller = perms.caller_info_strict()

	body_text: str | bytes = body
	blob_id = None

	if is_blob:
		if not settings.get_config('wopi:url'):
			raise BlobDocumentsNotSupported()

		# Create a blob and save it to the database.
		blob_id, ext = blob.create_blob(
			title + '.odt',
			['__docs'],
			True,
			True,
		)
		this_blob_path = blob.BlobStorage(blob_id, ext).path(create=True)
		with open('data/empty.odt', 'rb') as fp_from:
			with open(this_blob_path, 'wb') as fp_to:
				fp_to.write(fp_from.read())
		blob.add_reference(blob_id)
		size, md5sum = blob.file_info(this_blob_path)
		blob.mark_as_completed(blob_id, size, md5sum)

	doc = {
		'title': title,
		'body': body_text,
		'creator': caller.get('_id'),
		'created': datetime.now(UTC),
		'updated': None,
		'updater': None,
		'parent': None,
		'history': False,
		'previous': None,
		'blob_id': ObjectId(blob_id) if blob_id is not None else None,
		'tags': [],
		'shared_users': [],
		'shared_groups': [],
	}

	if doc['creator'] is None:
		doc['creator'] = caller.get('username')

	doc_id = db.insert_one(doc).inserted_id
	doc['_id'] = doc_id

	return parse_document(doc)


def link_document(title: str, blob_id: str) -> dict:
	"""
	Creates a new blob document linked to an already existing blob.

	Args:
		title (str): The title of the document.
		blob_id (str): The ID of the blob.

	Returns:
		dict: The new document.
	"""

	if not settings.get_config('wopi:url'):
		raise BlobDocumentsNotSupported()

	caller = perms.caller_info_strict()
	blob.add_reference(blob_id)

	doc = {
		'title': title,
		'body': '',
		'creator': caller.get('_id', caller.get('username')),
		'created': datetime.now(UTC),
		'updated': None,
		'updater': None,
		'parent': None,
		'history': False,
		'previous': None,
		'blob_id': ObjectId(blob_id),
		'tags': [],
		'shared_users': [],
		'shared_groups': [],
	}

	doc_id = db.insert_one(doc).inserted_id
	doc['_id'] = doc_id

	return parse_document(doc)


def update_document(
	doc_id: str,
	title: str | None,
	body: str | bytes | None,
	*,
	user_data: dict | None = None
) -> dict:
	"""
	Updates a document in the database.

	Args:
		doc_id (str): The ID of the document to update.
		title (str | None): The new title of the document. If None, the title is not updated.
		body (str | None): The new content of the document. If None, the body is not updated.

	Returns:
		dict: The updated document.
	"""

	if (doc := db.find_one({'_id': ObjectId(doc_id)})) is None:
		raise DocumentDoesNotExistError(doc_id)

	if title is None and body is None:
		# No change
		return parse_document(doc)

	blob_data = {}
	if doc['blob_id'] is not None:
		blob_data = blob.get_blob_data(doc['blob_id'])
		body_md5_old = blob_data['md5sum']
	else:
		body_md5_old = hashlib.md5(doc['body'].encode('utf8')).digest()
	body_text = '' if body is None else body
	body_md5_new = hashlib.md5(
		body_text.encode('utf8') if isinstance(body_text, str) else body_text
	).digest()  # type: ignore

	if title == doc['title'] and body_md5_old == body_md5_new:
		# No change
		return parse_document(doc)

	user_id: ObjectId = (
		perms.caller_info_strict() if user_data is None else user_data
	).get('_id')  # type: ignore

	doc['updated'] = datetime.now(UTC)
	doc['updater'] = user_id

	if title is not None:
		doc['title'] = title
	if body is not None:
		if doc['blob_id'] is None:
			doc['body'] = body
		else:
			with open(blob.BlobStorage(doc['blob_id'], blob_data['ext']).path(), 'wb') as fp:
				fp.write(body)  # type: ignore

	db.update_one({'_id': ObjectId(doc_id)}, {'$set': doc})

	return parse_document(doc)


def delete_document(doc_id: str) -> dict:
	"""
	Deletes a document from the database.

	Any history items get deleted.

	Args:
		doc_id (str): The ID of the document to delete.

	Returns:
		dict: The deleted document, if successful.
	"""

	id = ObjectId(doc_id)

	doc = db.find_one({'_id': id})
	if doc is None:
		raise DocumentDoesNotExistError(doc_id)

	if doc['blob_id'] is not None:
		blob.remove_reference(doc['blob_id'])

	db.delete_many({'parent': id})
	db.delete_one({'_id': id})

	return parse_document(doc)


def set_document_tags(doc_id: str, tags: list[str]) -> dict:
	"""
	Set tags for a document in the database.

	This function updates the tags for a document identified by its ID. If the document does not exist,
	it raises a BlobDoesNotExistError. The tags are converted to lowercase and duplicates are removed.

	Args:
		doc_id (str): The ID of the document to update.
		tags (list): A list of tags to set for the document.

	Returns:
		dict: The updated document data with the new tags.

	Raises:
		DocumentDoesNotExistError: If the document with the specified ID does not exist.
	"""
	if (doc := db.find_one({'_id': ObjectId(doc_id)})) is None:
		raise DocumentDoesNotExistError(doc_id)

	doc['tags'] = tags
	db.update_one({'_id': ObjectId(doc_id)}, {'$set': {'tags': tags}})

	return doc


def sum_document_size(filter: DocumentSearchFilter) -> int:
	"""
	Count the total size of all documents matching the filter.

	Args:
		filter (DocumentSearchFilter): Options for filtering documents.

	Returns:
		int: The total number of bytes the documents take up.
	"""
	total = 0

	# Count the text size in non-blob documents
	query_text = {
		'blob_id': None,
		**build_doc_query(filter),
	}
	aggregate_text = db.aggregate([
		{'$match': query_text},
		{
			'$group': {
				'_id': None,
				'total': {
					'$sum': '$size'
				}
			}
		}
	])
	for result in aggregate_text:
		total += result['total']

	# Count the blob size in blob documents
	query_blob = {
		'blob_id': {'$ne': None},
		**build_doc_query(filter),
	}
	aggregate_blob = db.aggregate([
		{'$match': query_blob},
		{
			'$lookup': {
				'from': 'blob',
				'localField': 'blob_id',
				'foreignField': '_id',
				'as': 'blob',
			}
		},
		{'$unwind': '$blob'},
		{
			'$group': {
				'_id': None,
				'total': {
					'$sum': '$blob.size'
				}
			}
		},
	])
	for result in aggregate_blob:
		total += result['total']

	return total


def zip_matching_documents(
	filter: DocumentSearchFilter,
	blob_zip_id: str
) -> dict:
	"""
	Create a ZIP archive of documents that match the given filter.

	Args:
		filter (BlobSearchFilter): The filter criteria to match blobs.
		blob_zip_id (str): A unique identifier for the ZIP archive.

	Returns:
		dict: Information about the created ZIP blob, including its ID.

	Raises:
		exceptions.BlobDoesNotExistError: If the created ZIP blob does not exist in the database.
	"""

	query = build_doc_query(filter)
	aggregate = db.aggregate([
		{'$match': query},
		{
			'$addFields': {
				'modified': {'$ifNull': ['$updated', '$created']},
			}
		},
		{'$sort': {'modified': 1}},
		{
			'$lookup': {
				'from': 'blob',
				'localField': 'blob_id',
				'foreignField': '_id',
				'as': 'blob',
			}
		},
	])

	filename = f'ARCHIVE-{blob_zip_id[-8::]}.zip'

	# Make sure that there's enough space for the zip file in the target location (+1MB for safety)
	total_size = sum_document_size(filter)
	dir_path = str(pathlib.Path(BlobStorage('', '').blob_path))
	if (total_size + 1024 * 1024) > shutil.disk_usage(dir_path).free:
		raise InsufficientDiskSpace()

	# Create the blob entry for the zip file.
	blob_zip_id = blob_zip_id.replace("/", "").replace("\\", "")
	id, ext = blob.create_blob(filename, [], hidden=True, ephemeral=True)
	this_blob_path = BlobStorage(id, ext).path(create=True)

	# Update DB to allow polling progress.
	blob.ZIP_PROGRESS[blob_zip_id] = [0, '', False, False]
	cancelled = False

	file_names = {}

	print('Creating ZIP archive of blob files.', flush=True)

	# Create a temp zip file
	with ZipFile(this_blob_path, 'w', compression=ZIP_DEFLATED, compresslevel=9) as fp:
		total = db.count_documents(query)
		item = 0

		for document in aggregate:
			item += 1

			if document.get('blob'):
				blob_data = document.get('blob')[0]
			else:
				blob_data = {
					'_id': document['_id'],
					'ext': '.md',
				}

			sub_blob = BlobStorage(blob_data['_id'], blob_data['ext'])

			file_name = document['title'] + blob_data['ext']
			if file_name in file_names:
				file_names[file_name] += 1
				file_name = f'{document["title"]} ({file_names[file_name]}){blob_data["ext"]}'
			else:
				file_names[file_name] = 0

			# If this zip action was cancelled, quit.
			if blob.ZIP_PROGRESS[blob_zip_id][2]:
				cancelled = True
				break

			# Update db to allow polling progress.
			blob.ZIP_PROGRESS[blob_zip_id] = [item / total, file_name, False, False]

			if not document.get('blob'):
				print(f'[{100 * item / total:.1f}%] Adding "{file_name}"...', flush=True)
				fp.writestr(file_name, document.get('body', ''))
			elif sub_blob.exists:
				print(f'[{100 * item / total:.1f}%] Adding "{file_name}"...', flush=True)
				fp.write(sub_blob.path(), file_name)
			else:
				msg = f'[{100 * item / total:.1f}%] ERROR: Blob {blob_data["_id"]}{blob_data["ext"]} does not exist!'
				print(msg, flush=True)

	print('ZIP archive was cancelled.' if cancelled else 'Finished ZIP archive.', flush=True)

	if cancelled:
		blob.delete_blob(id)
	else:
		size, md5sum = blob.file_info(this_blob_path)
		blob.mark_as_completed(id, size, md5sum)

	blob_data = blob.db.find_one({'_id': ObjectId(id)})
	if blob_data is None:
		print(f'ERROR: Blob {id} does not exist in the database after zipping!', flush=True)
		raise BlobDoesNotExistError(id)

	blob_data['id'] = blob_data['_id']

	blob.ZIP_PROGRESS[blob_zip_id][3] = True

	return blob_data


def share_with(id: str, my_groups: bool, specific_users: list[str]) -> dict:
	"""
	Share a document with specific users or the current user's group(s).

	Args:
		id (str): The ID of the document to update.
		my_groups (bool): Whether to share with all of this user's groups.
		specific_users (list[str]): The usernames of all users to explicitly share with.

	Returns:
		dict: The updated document.
	"""

	user_data = perms.caller_info_strict()

	doc = db.find_one({'_id': ObjectId(id)})
	if doc is None:
		raise DocumentDoesNotExistError(id)

	shared_users = []
	if len(specific_users) > 0:
		selection = users.db.find({
			'$or': [{'username': i} for i in specific_users]
		})
		shared_users = [i['_id'] for i in selection]

	update_doc = {
		'shared_groups': user_data.get('groups', []) if my_groups else [],
		'shared_users': shared_users,
	}

	db.update_one({'_id': ObjectId(id)}, {'$set': update_doc})

	return parse_document({
		**doc,
		**update_doc,
	})
