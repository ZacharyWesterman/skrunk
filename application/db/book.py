from application.tokens import decode_user_token, get_request_token
from application.db.settings import get_config, get_enabled_modules
import application.exceptions as exceptions
from application.objects import BookSearchFilter, Sorting
from . import users, blob
from application.integrations import google_books, subsonic
from datetime import datetime
from bson.objectid import ObjectId
import re, markdown

from pymongo.collection import Collection
db: Collection = None

SUBSONIC = None

_P = {
	'tag': re.compile(r'</?\w+>'),
	'nonwd': re.compile(r'[^\w]+'),
}

def init() -> None:
	global SUBSONIC

	url = get_config('subsonic:url')
	if url is not None and 'subsonic' in get_enabled_modules():
		username = get_config('subsonic:username')
		password = get_config('subsonic:password')
		SUBSONIC = subsonic.Session(url, username, password)
		try:
			print('Caching Subsonic data on startup...', flush=True)
			#Get albums on startup so it's cached for later use.
			SUBSONIC.all_albums('Audiobooks')

			#Cache as many album IDs as possible
			for book_data in db.find({}).limit(subsonic.SUBSONIC_ALBUMID_CACHESZ):
				SUBSONIC.get_album_id(book_data['title'], 'Audiobooks')

			print('Finished caching Subsonic data.', flush=True)
		except subsonic.SessionError:
			print('Unable to connect to Subsonic server!', flush=True)


def process_share_hist(share_history: list) -> list:
	share_hist = []
	for hist in share_history:
		if hist['user_id'] == None:
			hist['display_name'] = hist['name']
		else:
			try:
				shared_with = users.get_user_by_id(hist['user_id'])
			except exceptions.UserDoesNotExistError:
				shared_with = None

			hist['display_name'] = shared_with['display_name'] if shared_with is not None else hist['name']

		share_hist += [hist]

	return share_hist

def keyword_tokenize(text: str) -> list[str]:
	return list(set([
		i for i in _P['nonwd'].sub(' ', _P['tag'].sub(' ', text.replace('\'', ''))).lower().split() if len(i) > 2
	]))

def build_keywords(book_data: dict) -> list[str]:
	keywords = []
	for field in ['title', 'subtitle', 'description', 'authors']:
		field_data = book_data.get(field)
		if field_data is None: continue
		if type(field_data) is list:
			for i in field_data:
				keywords += keyword_tokenize(i)
		else:
			keywords += keyword_tokenize(field_data)

	return sorted(list(set(keywords)))

def process_book_tag(book_data: dict) -> dict:
	global SUBSONIC

	try:
		userdata = users.get_user_by_id(book_data['owner'])
		book_data['owner'] = userdata
	except exceptions.UserDoesNotExistError:
		book_data['owner'] = {
			'username': book_data['owner'],
			'display_name': book_data['owner'],
		}

	try:
		blobdata = blob.get_blob_data(book_data['thumbnail'])
		if blobdata:
			book_data['thumbnail'] = f'preview/{blobdata["thumbnail"]}'
	except exceptions.BlobDoesNotExistError:
		pass

	book_data['shareHistory'] = process_share_hist(book_data['shareHistory'])
	book_data['id'] = book_data['_id']
	book_data['keywords'] = build_keywords(book_data)
	book_data['audiobook'] = None

	if SUBSONIC:
		try:
			book_data['audiobook'] = SUBSONIC.get_album_id(book_data['title'], 'Audiobooks')
		except subsonic.SessionError:
			pass

	return book_data

def get_book_tag(rfid: str, *, parse: bool = False) -> dict:
	book_data = db.find_one({'rfid': rfid})

	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	return process_book_tag(book_data) if parse else book_data

def get_book(id: str, *, parse: bool = False) -> dict:
	book_data = db.find_one({'_id': ObjectId(id)})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(id)

	return process_book_tag(book_data) if parse else book_data

def next_out_of_date_book_rfid(before: datetime) -> str:
	book_data = db.find_one({'lastSync': {'$lt': before}})
	if book_data is None:
		return None

	return book_data['rfid']

def refresh_book_data(rfid: str) -> None:
	book_data = db.find_one({'rfid': rfid})

	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(rfid)

	google_book_data = google_books.get(id = book_data['bookId'])

	fields = ['title', 'subtitle', 'authors', 'publisher', 'publishedDate', 'description', 'industryIdentifiers', 'pageCount', 'categories', 'maturityRating', 'language', 'thumbnail']
	updated = {'lastSync': datetime.utcnow()}
	for i in fields:
		if i in book_data.get('noSyncFields', []):
			continue

		new_val = google_book_data.get(i)
		if new_val is not None and new_val != book_data[i]:
			updated[i] = new_val

	updated['keywords'] = build_keywords({**book_data, **updated})

	db.update_one({'rfid': rfid}, {'$set': updated})


def link_book_tag(owner: str, rfid: str, book_id: str) -> dict:
	if db.find_one({'rfid': rfid}):
		raise exceptions.BookTagExistsError(rfid)

	google_book_data = google_books.get(id = book_id)
	del google_book_data['id']

	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)
	owner_data = users.get_user_data(owner)

	book_data = {
		'rfid': rfid,
		'bookId': book_id,
		'creator': user_data['_id'],
		'owner': owner_data['_id'],
		'shared': False,
		'shareHistory': [],
		'lastSync': datetime.utcnow(),
		'created': datetime.utcnow(),
		'noSyncFields': [],
		'industryIdentifiers': google_book_data.get('industryIdentifiers', []),
		'ebooks': [],
	}
	fields = ['title', 'subtitle', 'authors', 'publisher', 'publishedDate', 'description', 'pageCount', 'categories', 'maturityRating', 'language', 'thumbnail']
	for i in fields:
		book_data[i] = google_book_data.get(i)

	book_data['keywords'] = build_keywords(book_data)

	db.insert_one(book_data)

	book_data['owner'] = user_data
	book_data['shareHistory'] = process_share_hist(book_data['shareHistory'])

	return book_data

def create_book(owner: str, data: dict) -> dict:
	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)
	owner_data = users.get_user_data(owner)

	book_data = {
		'rfid': data['rfid'],
		'bookId': None,
		'creator': user_data['_id'],
		'owner': owner_data['_id'],
		'shared': False,
		'shareHistory': [],
		'lastSync': datetime.utcnow(),
		'created': datetime.utcnow(),
		'noSyncFields': [],
		'industryIdentifiers': [],
		'title': data['title'],
		'subtitle': data['subtitle'],
		'authors': data['authors'],
		'publisher': data['publisher'],
		'publishedDate': data['publishedDate'],
		'description': None if data['description'] is None else markdown.markdown(data['description'], output_format = 'html'),
		'pageCount': data['pageCount'],
		'categories': [],
		'maturityRating': 'NOT_MATURE',
		'language': 'en',
		'thumbnail': data['thumbnail'].replace('http://', 'https://') if data['thumbnail'] else data['thumbnail'],
		'ebooks': [],
	}

	if data.get('isbn'):
		book_data['industryIdentifiers'] = [{
			'type': 'ISBN_' + str(len(data['isbn'])),
			'identifier': data['isbn'],
		}]

	book_data['keywords'] = build_keywords(book_data)

	db.insert_one(book_data)

	if book_data['thumbnail']:
		blob.add_reference(book_data['thumbnail'])

	return book_data


def unlink_book_tag(rfid: str) -> dict:
	book_data = db.find_one({'rfid': rfid})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	db.delete_one({'rfid': rfid})

	#Remove reference to this thumbnail if it uses a locally hosted blob.
	if book_data['thumbnail']:
		blob.remove_reference(book_data['thumbnail'])

	return book_data

def norm_query(query: dict, ownerq: dict|None) -> dict:
	if ownerq is not None:
		if query:
			return {'$and': [query, ownerq]}
		return ownerq
	return query

def build_book_query(filter: BookSearchFilter, sort: list = []) -> dict:
	query = {}
	aggregate = None

	owner = filter.get('owner')
	ownerq = None
	if owner is not None:
		if type(owner) is str:
			user_data = users.get_user_data(owner)
			query['owner'] = user_data['_id']
		elif len(owner):
			ownerq = {'$or': [{'owner': i} for i in owner]}

	if filter.get('author') is not None:
		query['authors'] = {'$regex': filter.get('author'), '$options': 'i'}

	if filter.get('genre') is not None:
		query['categories'] = {'$regex': filter.get('genre'), '$options': 'i'}

	if filter.get('shared') is not None:
		query['shared'] = filter.get('shared')

	if filter.get('title') is not None:
		isbn = filter.get('title').strip().replace('-', '')
		if re.match(r'^\d{9,13}$', isbn):
			query['industryIdentifiers.identifier'] = isbn
			query = norm_query(query, ownerq)
		else:
			keywords = keyword_tokenize(filter.get('title'))
			query['keywords'] = {'$in': keywords}
			query['score'] = {'$gt': (len(keywords)+1) // 2 if len(keywords) > 1 else 0 }
			query = norm_query(query, ownerq)

			aggregate = [
				{'$addFields': {
					'score': {
						'$size': {
							'$setIntersection': [keywords, '$keywords']
						}
					}
				}},
				{'$match': query},
				{'$sort': {'score': -1, **{i[0]:i[1] for i in sort} }}
			]
	else:
		query = norm_query(query, ownerq)

	return aggregate, query

def get_books(filter: BookSearchFilter, start: int, count: int, sorting: Sorting) -> list:
	global db
	books = []

	if 'title' not in sorting['fields']:
		sorting['fields'] += ['title']
	if 'authors' not in sorting['fields']:
		sorting['fields'] += ['authors']

	sort = [(i, -1 if sorting['descending'] else 1) for i in sorting['fields']]

	try:
		aggregate, query = build_book_query(filter, sort)
	except exceptions.UserDoesNotExistError:
		return []

	if aggregate:
		aggr_filter = [{'$facet': {'results': [{'$skip': start}, {'$limit': count}]}}]
		for i in db.aggregate(aggregate + aggr_filter):
			selection = i['results']
	else:
		selection = db.find(query, sort = sort).limit(count).skip(start)

	for i in selection:
		i = process_book_tag(i.get('results', i))
		books += [i]

	return books

def count_books(filter: BookSearchFilter) -> list:
	global db
	try:
		aggregate, query = build_book_query(filter)
	except exceptions.UserDoesNotExistError:
		return 0

	if aggregate:
		aggr_filter = [{'$facet': {'count': [{'$count': 'count'}]}}]
		for i in db.aggregate(aggregate + aggr_filter):
			ct = i['count']
			return ct[0]['count'] if len(ct) else 0
	else:
		return db.count_documents(query)

def share_book_with_user(book_id: str, username: str) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	user_data = users.get_user_data(username)

	if len(book_data['shareHistory']):
		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_id}, {'$set': updates})
	db.update_one({'_id': book_id}, {'$push': {'shareHistory': {
		'user_id': user_data['_id'],
		'name': username,
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data

def share_book_with_non_user(book_id: str, name: str) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if len(book_data['shareHistory']):
		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_id}, {'$set': updates})
	db.update_one({'_id': book_id}, {'$push': {'shareHistory': {
		'user_id': None,
		'name': name,
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data

def borrow_book(book_id: str, user_data: dict) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if len(book_data['shareHistory']):
		#If book is currently shared with a user OTHER THAN the one requesting to borrow, Throw an exception.
		#In that case, someone needs to declare that it is no longer being borrowed before it can be borrowed again.
		last_share = book_data['shareHistory'][-1]
		if last_share['stop'] is None and last_share['user_id'] != user_data['_id']:
			raise exceptions.BookCannotBeShared(f'This book is already being borrowed by {last_share["name"]}.')

		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_id}, {'$set': updates})
	db.update_one({'_id': book_id}, {'$push': {'shareHistory': {
		'user_id': user_data['_id'],
		'name': user_data['username'],
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data

def return_book(book_id: str, user_data: dict) -> dict:
	book_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if not book_data['shared']:
		raise exceptions.BookCannotBeShared('Nobody is borrowing this book.')

	last_share = len(book_data['shareHistory']) - 1
	if book_data['shareHistory'][-1]['user_id'] != user_data['_id'] and book_data['owner'] != user_data['_id']:
		raise exceptions.BookCannotBeShared('You did not borrow this book.')

	db.update_one({'_id': book_id}, {'$set': {'shared': False, f'shareHistory.{last_share}.stop': datetime.utcnow()}})
	return book_data

def set_book_owner(id: str, username: str) -> dict:
	book_data = get_book(id, parse = True)
	user_data = users.get_user_data(username)

	owner_hist = book_data.get('ownerHistory', [])
	if len(owner_hist):
		owner_hist[-1]['stop'] = datetime.utcnow()
	else:
		owner_hist = [{
			'user_id': book_data['owner'],
			'start': book_data['created'],
			'stop': datetime.utcnow(),
		}]
	owner_hist += [{
		'user_id': user_data['_id'],
		'start': datetime.utcnow(),
		'stop': None,
	}]

	book_data['owner'] = user_data['_id']

	db.update_one({'_id': ObjectId(id)}, {'$set': {'owner': user_data['_id']}})

	return book_data

def edit_book(id: str, new_data: dict) -> dict:
	book_data = get_book(id, parse = True)

	changed_fields = {}
	for i in new_data:
		if i in book_data and new_data[i] != book_data[i]:
			changed_fields[i] = new_data[i]
			book_data[i] = new_data[i]

	changed_fields['noSyncFields'] = list(set(book_data.get('noSyncFields',[]) + [i for i in changed_fields]))
	book_data['noSyncFields'] = changed_fields['noSyncFields']

	db.update_one({'_id': ObjectId(id)}, {'$set': changed_fields})

	return book_data

def count_all_user_books(filter_users: list|None = None) -> list:
	aggregate = db.aggregate([
		{ '$group': { '_id': '$owner', 'count': { '$sum': 1 } } }
	])

	result = []

	for i in aggregate:
		#Allow user group filtering
		if filter_users != None and i['_id'] not in filter_users:
			continue

		try:
			user_data = users.get_user_by_id(i['_id'])
			result += [{
				'owner': {
					'username': user_data['username'],
					'display_name': user_data['display_name'],
				},
				'count': i['count'],
			}]

		except exceptions.UserDoesNotExistError:
			#Just ignore users that no longer exist.
			pass

	return result

def append_ebook(book_id: str, ebook_url: str) -> dict:
	book_data = get_book(book_id)

	pos = ebook_url.rfind('.')
	ext = ebook_url[pos+1::] if pos > -1 else 'unk'

	book_data['ebooks'] += [{
		'url': ebook_url,
		'fileType': ext.lower(),
	}]

	db.update_one({'_id': ObjectId(book_id)}, {'$set': {'ebooks': book_data['ebooks']}})

	try:
		blob.get_blob_data(ebook_url)
		blob.add_reference(ebook_url) #If using blob id instead of file url, update the reference count.
	except exceptions.BlobDoesNotExistError:
		pass

	return book_data
