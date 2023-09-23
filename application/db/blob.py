from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
import application.tags as tags
from . import users
from application.integrations import models, images
from application.objects import BlobSearchFilter

from bson.objectid import ObjectId
from datetime import datetime
from zipfile import ZipFile, Path
import pathlib
import mimetypes
import hashlib
import uuid

db = None
blob_path = None

class BlobStorage:
	def __init__(self, id: str, ext: str = ''):
		self.id = id
		self.ext = ext

	def path(self, *, create: bool = False) -> str:
		global blob_path
		full_path = f'{blob_path}/{self.id[0:2]}/{self.id[2:4]}'
		if create:
			pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)

		return f'{full_path}/{self.basename()}'

	def basename(self) -> str:
		return f'{self.id}{self.ext}'

class BlobPreview(BlobStorage):
	def __init__(self, id: str, ext: str = ''):
		super().__init__(f'{id}_p' if ext != '' else str(id), ext)

class BlobThumbnail(BlobStorage):
	def __init__(self, id: str, ext: str = ''):
		super().__init__(f'{id}_t' if ext != '' else str(id), ext)



def file_info(filename: str) -> str:
	with open(filename, 'rb') as fp:
		md5sum = hashlib.md5(fp.read()).hexdigest()
	size = pathlib.Path(filename).stat().st_size

	return size, md5sum

def save_blob_data(file: object, auto_unzip: bool, tags: list = []) -> list:
	global blob_path
	filename = file.filename
	id, ext = create_blob(filename, tags)
	this_blob_path = BlobStorage(id, ext).path(create = True)

	print(f'Beginning stream of file "{filename}"...')
	file.save(this_blob_path)
	print(f'Finished stream of file "{filename}".')

	uploaded_blobs = []

	if auto_unzip and ext == '.zip':
		print(f'Unzipping file "{filename}"...')
		extract_count = 0
		with ZipFile(this_blob_path, 'r') as fp:
			for name in fp.namelist():
				print('Extracting ' + name, flush=True)
				item = Path(fp, name)
				if item.is_dir(): continue

				#directly create new blobs from each item in the zip file
				id2, ext2 = create_blob(name, tags)
				inner_blob_path = BlobStorage(id2, ext2).path(create = True)
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

	#Create file previews
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
			create_preview(this_blob_path, blob['id'])

	return uploaded_blobs

def get_tags_from_mime(mime: str) -> list:
	return [ i for i in mime.split('/') ]

def set_mime_from_ext(mime: str, ext: str) -> str:
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

	return mime


def create_blob(name: str, tags: list = []) -> str:
	global db

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

	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

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
	}).inserted_id), ext

def mark_as_completed(id: str, size: int, md5sum: str) -> None:
	db.update_one({'_id': ObjectId(id)}, {'$set': {'complete': True, 'size': size, 'md5sum': md5sum}})

def build_blob_query(filter: BlobSearchFilter) -> dict:
	query = []

	if filter.get('tag_expr') is not None:
		tag_q = tags.parse(filter.get('tag_expr')).output()
		if tag_q:
			query += [tag_q]

	if type(filter.get('creator')) is str:
		user_data = users.get_user_data(filter.get('creator'))
		query += [{'creator': user_data['_id']}]

	if filter.get('begin_date') is not None:
		query += [{'created': {'$gte': filter.get('begin_date')}}]

	if filter.get('end_date') is not None:
		query += [{'created': {'$lte': filter.get('end_date')}}]

	if filter.get('name') is not None:
		query += [{'name': {'$regex': filter.get('name'), '$options': 'i'}}]

	creator = filter.get('creator')
	if type(creator) is list and len(creator):
		query += [{'$or': [{'creator': i} for i in creator]}]

	return {'$and': query} if len(query) else {}

def get_blobs(filter: BlobSearchFilter, start: int, count: int) -> list:
	global db
	try:
		query = build_blob_query(filter)
	except exceptions.UserDoesNotExistError:
		return []

	blobs = []

	selection = db.find(query, sort=[('created', -1)])
	for i in selection.limit(count).skip(start):
		i['id'] = i['_id']
		try:
			user_data = users.get_user_by_id(i['creator'])
			i['creator'] = user_data['username']
		except exceptions.UserDoesNotExistError:
			i['creator'] = str(i['creator'])
		blobs += [i]

	return blobs

def count_blobs(filter: BlobSearchFilter) -> int:
	global db

	try:
		query = build_blob_query(filter)
	except exceptions.UserDoesNotExistError:
		return 0

	return db.count_documents(query)

def sum_blob_size(filter: BlobSearchFilter) -> int:
	try:
		query = build_blob_query(filter)
	except exceptions.UserDoesNotExistError:
		return 0

	aggregate = db.aggregate([{
		'$match': query
	},{
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

def zip_matching_blobs(filter: BlobSearchFilter) -> dict:
	query = build_blob_query(filter)
	if query:
		query['$and'] += [{'complete': True}]
	else:
		query = {'complete': True}

	id, ext = create_blob(f'ARCHIVE-{uuid.uuid4()}.zip', [])
	this_blob_path = BlobStorage(id, ext).path(create = True)

	file_names = {}

	with ZipFile(this_blob_path, 'w') as fp:
		for blob in db.find(query):
			print(f'Adding {blob["_id"]} to ZIP archive...', flush=True)
			sub_blob = BlobStorage(blob['_id'], blob['ext'])

			file_name = sub_blob.basename()
			if file_name in file_names:
				file_names[file_name] += 1
				file_name = f'{blob["name"]} ({file_names[file_name]}){blob["ext"]}'
			else:
				file_names[file_name] = 0

			fp.write(sub_blob.path(), file_name)

	print('Finished ZIP archive.', flush=True)

	size, md5sum = file_info(this_blob_path)
	mark_as_completed(id, size, md5sum)

	blob = db.find_one({'_id': ObjectId(id)})
	blob['id'] = blob['_id']
	return blob


def get_blob_data(blob_id: str) -> dict:
	global db
	blob_data = db.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		blob_data['id'] = blob_data['_id']
		try:
			user_data = users.get_user_by_id(blob_data['creator'])
			blob_data['creator'] = user_data['username']
		except exceptions.UserDoesNotExistError:
			blob_data['creator'] = str(blob_data['creator'])
	return blob_data

def delete_blob(blob_id: str) -> bool:
	global db
	blob_data = db.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		try:
			item = pathlib.Path(BlobStorage(blob_id, blob_data['ext']).path())
			item.unlink()
		except FileNotFoundError:
			pass

		if blob_data.get('preview') is not None:
			try:
				prevw = pathlib.Path(BlobPreview(blob_data['preview']).path())
				prevw.unlink()
			except FileNotFoundError:
				pass

		#Delete volume dirs if empty
		try:
			item.parent.rmdir()
			item.parent.parent.rmdir()
		except OSError:
			pass

		db.delete_one({'_id': ObjectId(blob_id)})
		return blob_data

	raise exceptions.BlobDoesNotExistError(blob_id)

def set_blob_tags(blob_id: str, tags: list) -> dict:
	global db
	blob_data = db.find_one({'_id': ObjectId(blob_id)})
	if not blob_data:
		raise exceptions.BlobDoesNotExistError(blob_id)

	tags = [ i.lower() for i in list(set(tags)) ]

	db.update_one({'_id': ObjectId(blob_id)}, {'$set': {'tags': tags}})
	blob_data['tags'] = tags
	return blob_data

def create_preview(blob_path: str, preview_id: str) -> None:
	preview = BlobPreview(preview_id, '.glb')
	models.to_glb(blob_path, preview.path())
	db.update_one({'_id': ObjectId(preview_id)}, {'$set': {'preview': preview.basename()}})
