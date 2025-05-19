"""application.db.blob"""

import application.exceptions as exceptions
import application.tags as tags
from . import users
from application.integrations import models, images, videos
from application.objects import BlobSearchFilter, Sorting
from werkzeug.datastructures import FileStorage
from application.types import BlobStorage, BlobPreview, BlobThumbnail
from application import types
from .perms import caller_info

from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from zipfile import ZipFile, Path
import pathlib
import mimetypes
import hashlib
import uuid
import shutil

from pymongo.collection import Collection

## A pointer to the Blob collection in the database.
db: Collection = None  # type: ignore[assignment]

## The path to the blob storage directory.
blob_path: str | None = None

## A dictionary to store the progress of ZIP operations.
_zip_progress = {}


def init() -> None:
	"""
	Initializes the blob module by setting the global blob_path and deleting
	all ephemeral files that are not referred to by any data.

	Note:
		This function should be called on startup, and regular restarts should
		be scheduled to ensure that ephemeral files are cleaned up.
	"""
	global blob_path
	blob_path = types.blob_path

	# On startup, delete all ephemeral files which aren't referred to by any data.
	# Restart should be scheduled regularly for this to apply
	deleted_ct = 0

	for i in db.find({'ephemeral': True, 'references': 0}):
		delete_blob(i['_id'])
		deleted_ct += 1

	if deleted_ct:
		print(f'Deleted {deleted_ct} ephemeral blob entries.', flush=True)


def file_info(filename: str) -> tuple[int, str]:
	"""
	Calculate the MD5 checksum and size of a file.

	Args:
		filename (str): The path to the file.

	Returns:
		tuple: A tuple containing the size of the file in bytes (int) and the MD5 checksum (str).
	"""
	with open(filename, 'rb') as fp:
		md5sum = hashlib.md5(fp.read()).hexdigest()
	size = pathlib.Path(filename).stat().st_size

	return size, md5sum


def save_blob_data(file: FileStorage, auto_unzip: bool, tags: list = [], hidden: bool = False, ephemeral: bool = False) -> list:
	"""
	Save blob data to storage and optionally unzip if the file is a zip archive.

	Args:
		file (FileStorage): The file to be saved.
		auto_unzip (bool): If True, automatically unzip the file if it is a zip archive.
		tags (list, optional): List of tags to associate with the blob. Defaults to [].
		hidden (bool, optional): If True, mark the blob as hidden. Defaults to False.
		ephemeral (bool, optional): If True, mark the blob as ephemeral. Defaults to False.

	Returns:
		list: A list of dictionaries containing the unique ID and file extension of the uploaded blobs.
	"""
	filename = '<unknown>' if file.filename is None else file.filename
	id, ext = create_blob(filename, tags, hidden and not (auto_unzip and filename.lower().endswith('.zip')), ephemeral)
	this_blob_path = BlobStorage(id, ext).path(create=True)

	print(f'Beginning stream of file "{filename}"...', flush=True)
	file.save(this_blob_path)
	print(f'Finished stream of file "{filename}".', flush=True)

	uploaded_blobs = []

	if auto_unzip and ext == '.zip':
		print(f'Unzipping file "{filename}"...')
		extract_count = 0
		with ZipFile(this_blob_path, 'r') as fp:
			for name in fp.namelist():
				print('Extracting ' + name, flush=True)
				item = Path(fp, name)
				if item.is_dir():
					continue

				# directly create new blobs from each item in the zip file
				id2, ext2 = create_blob(name, tags, hidden, ephemeral)
				inner_blob_path = BlobStorage(id2, ext2).path(create=True)
				with fp.open(name, 'r') as input:
					with open(inner_blob_path, 'wb') as output:
						output.write(input.read())
				size, md5sum = file_info(inner_blob_path)
				mark_as_completed(id2, size, md5sum)
				extract_count += 1

				uploaded_blobs += [{'id': id2, 'ext': ext2}]

		print(f'Finished unzipping "{filename}" (extracted {extract_count} files).')
		delete_blob(id)
	else:
		size, md5sum = file_info(this_blob_path)
		mark_as_completed(id, size, md5sum)
		uploaded_blobs += [{'id': id, 'ext': ext}]

	# Create file previews
	for blob in uploaded_blobs:
		if blob['ext'].lower() in images.extensions():
			this_blob_path = BlobStorage(blob['id'], blob['ext']).path()
			preview = BlobPreview(blob['id'], blob['ext'])
			if images.downscale(this_blob_path, 512, preview.path()):
				db.update_one({'_id': ObjectId(blob['id'])}, {'$set': {'preview': preview.basename()}})

			thumbnail = BlobThumbnail(blob['id'], blob['ext'])
			if images.downscale(this_blob_path, 128, thumbnail.path()):
				db.update_one({'_id': ObjectId(blob['id'])}, {'$set': {'thumbnail': thumbnail.basename()}})

		elif blob['ext'].lower() in models.extensions():
			this_blob_path = BlobStorage(blob['id'], blob['ext']).path()
			create_preview_model(this_blob_path, blob['id'])

		elif blob['ext'].lower() in videos.extensions():
			this_blob_path = BlobStorage(blob['id'], blob['ext']).path()
			create_preview_video(this_blob_path, blob['id'])

	return uploaded_blobs


def get_tags_from_mime(mime: str) -> list:
	"""
	Extracts tags from a MIME type string.

	Args:
		mime (str): The MIME type string to be split into tags.

	Returns:
		list: A list of tags obtained by splitting the MIME type string by '/'.
	"""
	return [i for i in mime.split('/')]


def set_mime_from_ext(mime: str, ext: str) -> str:
	"""
	Sets the MIME type based on the file extension.

	Args:
		mime (str): The initial MIME type.
		ext (str): The file extension.

	Returns:
		str: The updated MIME type based on the file extension.
	"""
	documents = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.rtf', '.odf']
	source = ['.c', '.cpp', '.h', '.hpp', '.py', '.html', '.xml', '.xhtml', '.htm', '.sh', '.bat', '.java', '.js', '.css', '.md', '.glsl']

	mime = mime.replace('application/', '')

	if ext in models.extensions():
		mime = f'model/{ext[1::]}'
	elif ext in documents:
		mime = f'document/{ext[1::]}'
	elif ext in source:
		mime = f'text/code/{ext[1::]}'
	elif ext == '.msi':
		mime = 'application/installer/msi/binary'
	elif ext == '.exe':
		mime = 'application/exe/binary'
	elif ext == '.db':
		mime = 'binary/database'
	elif mime == 'octet-stream':
		mime = 'binary/unknown'
	elif mime == 'application/epub+zip':
		mime = 'ebook/epub'

	return mime


def create_blob(name: str, tags: list = [], hidden: bool = False, ephemeral: bool = False) -> tuple[str, str]:
	"""
	Creates a new blob entry in the database.

	Args:
		name (str): The name of the blob, typically the filename.
		tags (list, optional): A list of tags associated with the blob. Defaults to an empty list.
		hidden (bool, optional): A flag indicating if the blob should be hidden. Defaults to False.
		ephemeral (bool, optional): A flag indicating if the blob is ephemeral. Defaults to False.

	Returns:
		tuple[str, str]: A tuple containing the inserted blob's ID and the file extension.
	"""
	mime = mimetypes.guess_type(name)[0]

	if mime is None:
		mime = 'application/octet-stream'

	pos = name.rfind('.')
	ext = name[pos::] if pos > -1 else ''
	name = name[0:pos] if pos > -1 else name

	if ext == '.webp':
		mime = 'image/webp'

	real_mime = mime
	mime = set_mime_from_ext(mime, ext.lower()).lower()

	user_data = caller_info()
	if user_data is None:
		raise exceptions.AuthenticationError()

	auto_tags = get_tags_from_mime(mime)

	return str(db.insert_one({
		'created': datetime.utcnow(),
		'name': name,
		'ext': ext,
		'mimetype': real_mime,
		'size': 0,
		'tags': list(set(tags + auto_tags)),
		'creator': user_data['_id'],
		'complete': False,
		'preview': None,
		'thumbnail': None,
		'hidden': hidden,
		'ephemeral': ephemeral,
		'references': 0,
	}).inserted_id), ext


def mark_as_completed(id: str, size: int, md5sum: str) -> None:
	"""
	Marks a blob as completed in the database.

	Args:
		id (str): The unique identifier of the blob.
		size (int): The size of the blob in bytes.
		md5sum (str): The MD5 checksum of the blob.

	Returns:
		None
	"""
	db.update_one({'_id': ObjectId(id)}, {'$set': {'complete': True, 'size': size, 'md5sum': md5sum}})


def build_blob_query(filter: BlobSearchFilter, user_id: ObjectId) -> dict:
	"""
	Builds a MongoDB query for searching blobs based on the provided filter and user ID.

	Args:
		filter (BlobSearchFilter): A filter object containing various search criteria.
		user_id (ObjectId): The ID of the user making the query.

	Returns:
		dict: A MongoDB query dictionary constructed based on the provided filter and user ID.

	The filter object can contain the following keys:
		- tag_expr (str): A tag expression to filter blobs by tags.
		- creator (str or list): A username or a list of usernames to filter blobs by their creators.
		- begin_date (datetime): The start date to filter blobs created after this date.
		- end_date (datetime): The end date to filter blobs created before this date.
		- name (str): A regex pattern to filter blobs by their names.
		- ephemeral (bool): A boolean to filter blobs by their ephemeral status.

	The query will always include blobs that are either not hidden or created by the user.
	"""
	query = [{
		'$or': [
			{'hidden': False},
			{'creator': user_id},
		]
	}]

	tag_expr = filter.get('tag_expr')
	if tag_expr is not None:
		tag_q = tags.parse(tag_expr).output()
		if tag_q:
			query += [tag_q]

	creator = filter.get('creator')
	if type(creator) is str:
		user_data = users.get_user_data(creator)
		query += [{'creator': user_data['_id']}]

	if filter.get('begin_date') is not None:
		query += [{'created': {'$gte': filter.get('begin_date')}}]

	if filter.get('end_date') is not None:
		query += [{'created': {'$lte': filter.get('end_date')}}]

	if filter.get('name') is not None:
		query += [{'name': {'$regex': filter.get('name'), '$options': 'i'}}]

	if filter.get('ephemeral') is not None:
		query += [{'ephemeral': filter.get('ephemeral')}]

	creator = filter.get('creator')
	if type(creator) is list and len(creator):
		query += [{'$or': [{'creator': i} for i in creator]}]

	return {'$and': query} if len(query) else {}


def get_blobs(filter: BlobSearchFilter, start: int, count: int, sorting: Sorting, user_id: ObjectId) -> list:
	"""
	Retrieve a list of blobs from the database based on the provided filter, pagination, and sorting options.

	Args:
		filter (BlobSearchFilter): The filter criteria to apply to the blob search.
		start (int): The starting index for pagination.
		count (int): The number of blobs to retrieve.
		sorting (Sorting): The sorting options for the blobs.
		user_id (ObjectId): The ID of the user performing the search.

	Returns:
		list: A list of blobs matching the search criteria.
	"""
	try:
		query = build_blob_query(filter, user_id)
	except exceptions.UserDoesNotExistError:
		return []

	blobs = []

	if 'created' not in sorting['fields']:
		sorting['fields'] += ['created']

	sort = [(i, -1 if sorting['descending'] else 1) for i in sorting['fields']]

	selection = db.find(query, sort=sort)
	for i in selection.limit(count).skip(start):
		i['id'] = i['_id']
		try:
			user_data = users.get_user_by_id(i['creator'])
			i['creator'] = user_data['username']
		except exceptions.UserDoesNotExistError:
			i['creator'] = str(i['creator'])
		blobs += [i]

	return blobs


def count_blobs(filter: BlobSearchFilter, user_id: ObjectId) -> int:
	"""
	Count the number of blobs in the database that match the given filter and user ID.

	Args:
		filter (BlobSearchFilter): The filter criteria to apply to the blob search.
		user_id (ObjectId): The ID of the user whose blobs are being counted.

	Returns:
		int: The number of blobs that match the filter criteria for the given user.
	"""
	try:
		query = build_blob_query(filter, user_id)
	except exceptions.UserDoesNotExistError:
		return 0

	return db.count_documents(query)


def sum_blob_size(filter: BlobSearchFilter, user_id: ObjectId) -> int:
	"""
	Calculate the total size of blobs that match the given filter for a specific user.

	Args:
		filter (BlobSearchFilter): The filter criteria to search for blobs.
		user_id (ObjectId): The ID of the user whose blobs are being queried.

	Returns:
		int: The total size of the blobs that match the filter. Returns 0 if the user does not exist or no blobs match the filter.
	"""
	try:
		query = build_blob_query(filter, user_id)
	except exceptions.UserDoesNotExistError:
		return 0

	aggregate = db.aggregate([{
		'$match': query
	}, {
		'$group': {
			'_id': None,
			'total': {
				'$sum': '$size'
			}
		}
	}])

	for result in aggregate:
		return result['total']

	return 0


def get_uid() -> str:
	"""
	Generate a unique identifier (UID).

	This function generates a new unique identifier using the UUID version 4 standard,
	which creates a random UUID.

	Returns:
		str: A string representation of the generated UUID.
	"""
	return str(uuid.uuid4())


def zip_matching_blobs(filter: BlobSearchFilter, user_id: ObjectId, blob_zip_id: str) -> dict:
	"""
	Create a ZIP archive of blobs that match the given filter and user ID.

	Args:
		filter (BlobSearchFilter): The filter criteria to match blobs.
		user_id (ObjectId): The ID of the user requesting the ZIP archive.
		blob_zip_id (str): A unique identifier for the ZIP archive.

	Returns:
		dict: Information about the created ZIP blob, including its ID.

	Raises:
		exceptions.BlobDoesNotExistError: If the created ZIP blob does not exist in the database.
	"""
	global _zip_progress

	query = build_blob_query(filter, user_id)
	if query:
		query['$and'] += [{'complete': True}]
	else:
		query = {'complete': True}

	filename = f'ARCHIVE-{blob_zip_id[-8::]}.zip'
	temp_filename = f'/tmp/{filename}'

	# Make sure that there's enough space in /tmp for the zip file (+1MB for safety)
	total_size = sum_blob_size(filter, user_id)
	if (total_size + 1024 * 1024) > shutil.disk_usage('/tmp').free:
		raise exceptions.InsufficientDiskSpace()

	# Create the blob entry for the zip file.
	blob_zip_id = blob_zip_id.replace("/", "").replace("\\", "")
	id, ext = create_blob(filename, [], ephemeral=True)
	this_blob_path = BlobStorage(id, ext).path(create=True)

	# Update DB to allow polling progress.
	_zip_progress[blob_zip_id] = [0, '', False, False]
	cancelled = False

	file_names = {}

	print('Creating ZIP archive of blob files.', flush=True)

	# Create a temp zip file
	with ZipFile(temp_filename, 'w') as fp:
		total = db.count_documents(query)
		item = 0

		for blob in db.find(query):
			item += 1

			sub_blob = BlobStorage(blob['_id'], blob['ext'])

			file_name = blob['name'] + blob['ext']
			if file_name in file_names:
				file_names[file_name] += 1
				file_name = f'{blob["name"]} ({file_names[file_name]}){blob["ext"]}'
			else:
				file_names[file_name] = 0

			# If this zip action was cancelled, quit.
			if _zip_progress[blob_zip_id][2]:
				cancelled = True
				break

			# Update db to allow polling progress.
			_zip_progress[blob_zip_id] = [item / total, file_name, False, False]

			if sub_blob.exists:
				print(f'[{100 * item / total:.1f}%] Adding "{file_name}"...', flush=True)
				fp.write(sub_blob.path(), file_name)
			else:
				print(f'[{100 * item / total:.1f}%] ERROR: Blob {blob["_id"]}{blob["ext"]} does not exist!', flush=True)

	print('ZIP archive was cancelled.' if cancelled else 'Finished ZIP archive.', flush=True)

	_zip_progress[blob_zip_id][3] = True

	if cancelled:
		delete_blob(id)
		# Remove the temp file
		# linter complains that Path.unlink() doesn't exist, but it does
		Path(temp_filename).unlink(missing_ok=True)  # type: ignore[union-attr]
	else:
		# Move the temp file to the blob storage path
		shutil.move(temp_filename, this_blob_path)
		print('Moved temp file to blob storage path.', flush=True)

	size, md5sum = file_info(this_blob_path)
	mark_as_completed(id, size, md5sum)

	blob = db.find_one({'_id': ObjectId(id)})
	if blob is None:
		raise exceptions.BlobDoesNotExistError(id)

	blob['id'] = blob['_id']
	return blob


def cancel_zip(blob_zip_id: str) -> dict:
	"""
	Cancels the zip operation for the given blob_zip_id.

	Args:
		blob_zip_id (str): The ID of the blob zip operation to cancel.

	Raises:
		BlobDoesNotExistError: If the blob_zip_id does not exist in the _zip_progress.

	Returns:
		dict: A dictionary containing the progress and item of the zip operation.
	"""
	global _zip_progress

	if blob_zip_id not in _zip_progress:
		raise exceptions.BlobDoesNotExistError(blob_zip_id)

	_zip_progress[blob_zip_id][2] = True
	progress = _zip_progress[blob_zip_id]

	return {
		'progress': progress[0],
		'item': progress[1],
	}


def get_zip_progress(blob_zip_id: str) -> dict:
	"""
	Retrieve the progress of a zip operation by its ID.

	Args:
		blob_zip_id (str): The ID of the zip operation.

	Returns:
		dict: A dictionary containing the progress and the current item being processed.

	Raises:
		BlobDoesNotExistError: If the provided blob_zip_id does not exist in the progress tracking.
	"""
	if blob_zip_id not in _zip_progress:
		raise exceptions.BlobDoesNotExistError(blob_zip_id)

	progress = _zip_progress[blob_zip_id]

	return {
		'progress': progress[0],
		'item': progress[1],
		'finalizing': progress[3],
	}


def get_blob_data(id: str) -> dict:
	"""
	Retrieve blob data from the database by its ID.

	Args:
		id (str): The ID of the blob to retrieve.

	Returns:
		dict: A dictionary containing the blob data. If the blob exists, the dictionary
			will include the blob's ID and the creator's username. If the creator does
			not exist, the creator field will contain the creator's ID as a string.

	Raises:
		exceptions.BlobDoesNotExistError: If the blob with the given ID does not exist.
	"""
	global db
	try:
		blob_data = db.find_one({'_id': ObjectId(id)})
	except InvalidId:
		raise exceptions.BlobDoesNotExistError(id)

	if blob_data is None:
		raise exceptions.BlobDoesNotExistError(id)

	blob_data['id'] = blob_data['_id']
	try:
		user_data = users.get_user_by_id(blob_data['creator'])
		blob_data['creator'] = user_data['username']
	except exceptions.UserDoesNotExistError:
		blob_data['creator'] = str(blob_data['creator'])

	return blob_data


def delete_blob(blob_id: str) -> dict:
	"""
	Deletes a blob from the database and the file system.

	Args:
		blob_id (str): The ID of the blob to be deleted.

	Returns:
		dict: The data of the deleted blob.

	Raises:
		BlobDoesNotExistError: If the blob with the given ID does not exist.
	"""
	blob_data: dict | None = db.find_one({'_id': ObjectId(blob_id)})
	if blob_data is not None:
		# Delete the preview file if it exists
		if blob_data.get('preview') is not None:
			try:
				prevw = pathlib.Path(BlobPreview(blob_data['preview'], '').path(), '')
				prevw.unlink()
			except FileNotFoundError:
				pass

		# Delete the thumbnail file if it exists
		if blob_data.get('thumbnail') is not None:
			try:
				thumb = pathlib.Path(BlobThumbnail(blob_data['thumbnail'], '').path(), '')
				thumb.unlink()
			except FileNotFoundError:
				pass

		try:
			# Delete the blob from disk
			item = pathlib.Path(BlobStorage(blob_id, blob_data['ext']).path())
			item.unlink()

			# Delete volume dirs if empty
			item.parent.rmdir()
			item.parent.parent.rmdir()
		except FileNotFoundError | OSError:
			pass

		db.delete_one({'_id': ObjectId(blob_id)})
		return blob_data

	raise exceptions.BlobDoesNotExistError(blob_id)


def set_blob_tags(blob_id: str, tags: list) -> dict:
	"""
	Set tags for a blob in the database.

	This function updates the tags for a blob identified by its ID. If the blob does not exist,
	it raises a BlobDoesNotExistError. The tags are converted to lowercase and duplicates are removed.

	Args:
		blob_id (str): The ID of the blob to update.
		tags (list): A list of tags to set for the blob.

	Returns:
		dict: The updated blob data with the new tags.

	Raises:
		BlobDoesNotExistError: If the blob with the specified ID does not exist.
	"""
	blob_data = db.find_one({'_id': ObjectId(blob_id)})
	if not blob_data:
		raise exceptions.BlobDoesNotExistError(blob_id)

	tags = [i.lower() for i in list(set(tags))]

	db.update_one({'_id': ObjectId(blob_id)}, {'$set': {'tags': tags}})
	blob_data['tags'] = tags
	return blob_data


def set_blob_ephemeral(blob_id: str, ephemeral: bool) -> dict:
	"""
	Sets the 'ephemeral' status of a blob in the database and returns the updated blob data.

	Args:
		blob_id (str): The unique identifier of the blob.
		ephemeral (bool): The new ephemeral status to set for the blob.

	Returns:
		dict: The updated blob data with the new ephemeral status.
	"""
	blob_data = get_blob_data(blob_id)

	db.update_one({'_id': ObjectId(blob_id)}, {'$set': {'ephemeral': ephemeral}})
	blob_data['ephemeral'] = ephemeral
	return blob_data


def create_preview_model(blob_path: str, preview_id: str) -> None:
	"""
	Creates a preview model from a blob and updates the database with the preview information.

	Args:
		blob_path (str): The file path to the blob.
		preview_id (str): The unique identifier for the preview.

	Returns:
		None
	"""
	preview = BlobPreview(preview_id, '.glb')
	models.to_glb(blob_path, preview.path())
	db.update_one({'_id': ObjectId(preview_id)}, {'$set': {'preview': preview.basename()}})


def create_preview_video(blob_path: str, preview_id: str) -> None:
	"""
	Creates a preview video from the first frame of the given video blob and updates the database with the preview information.

	Args:
		blob_path (str): The file path to the video blob.
		preview_id (str): The unique identifier for the preview.

	Returns:
		None
	"""
	preview = BlobPreview(preview_id, '.png')
	videos.create_preview_from_first_frame(blob_path, preview.path())
	db.update_one({'_id': ObjectId(preview_id)}, {'$set': {'preview': preview.basename()}})


def set_blob_hidden(blob_id: str, hidden: bool) -> dict:
	"""
	Set the hidden status of a blob in the database.

	Args:
		blob_id (str): The unique identifier of the blob.
		hidden (bool): The hidden status to set for the blob.

	Returns:
		dict: The updated blob data.

	Raises:
		BlobDoesNotExistError: If the blob with the given ID does not exist.
	"""
	blob_data = get_blob_data(blob_id)
	if not blob_data:
		raise exceptions.BlobDoesNotExistError(blob_id)

	db.update_one({'_id': ObjectId(blob_id)}, {'$set': {'hidden': hidden}})
	blob_data['hidden'] = hidden

	return blob_data


def count_tag_uses(tag: str, users: list[str]) -> int:
	"""
	Count the number of documents in the database that contain a specific tag and are created by any of the specified users.

	Args:
		tag (str): The tag to search for in the documents.
		users (list[str]): A list of user identifiers to filter the documents by their creators.

	Returns:
		int: The count of documents that match the specified tag and creators.
	"""
	return db.count_documents({'$and': [{'tags': tag}, {'$or': [{'creator': i} for i in users]}]})


def add_reference(id: str) -> None:
	"""
	Increment the 'references' field of a document in the database by 1.

	Args:
		id (str): The unique identifier of the document to update.

	Returns:
		None
	"""
	db.update_one({'_id': ObjectId(id)}, {'$inc': {'references': 1}})


def remove_reference(id: str) -> None:
	"""
	Decrements the reference count of a database object identified by the given ID.

	If the provided ID is not a valid ObjectId, the function returns immediately.
	Otherwise, it decrements the 'references' field of the object by 1 and ensures
	that the 'references' field does not go below 0.

	Args:
		id (str): The ID of the database object whose reference count is to be decremented.

	Returns:
		None
	"""
	# If an invalid objectID, then there couldn't possibly be any references to it.
	if not ObjectId.is_valid(id):
		return

	db.update_one({'_id': ObjectId(id)}, {'$inc': {'references': -1}})
	db.update_one({'_id': ObjectId(id)}, {'$min': {'references': 0}})
