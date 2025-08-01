"""application.db.book"""

import re
import string
from datetime import datetime

import markdown
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from application import exceptions
from application.db.settings import get_config
from application.integrations import (get_subsonic, google_books,
                                      init_subsonic, subsonic)
from application.types import BookSearchFilter, Sorting

from . import blob, users
from .perms import caller_info_strict

## A pointer to the Book collection in the database.
db: Collection = None  # type: ignore[assignment]

subsonic_albums: list = []
subsonic_albums_complete: bool = False
subsonic_albums_page: int = 0

## Regular expressions used for extracting keywords from text.
_P = {
	'tag': re.compile(r'</?\w+>'),
	'nonwd': re.compile(r'[^\w]+'),
}


def init() -> None:
	"""
	Initialize the application by pre-caching some data.
	"""
	try:
		client = get_subsonic()
		if client is None:
			client = subsonic_init()

		print('Pre-caching Subsonic albums... ', flush=True, end='')

		# If this title is not in the album cache, then fetch more
		global subsonic_albums_complete, subsonic_albums_page, subsonic_albums
		while not subsonic_albums_complete:
			albums = client.albums('Audiobooks', subsonic_albums_page, 40)
			subsonic_albums += albums

			subsonic_albums_page += 1
			if len(albums) < 40:
				subsonic_albums_complete = True

		print('Done.', flush=True)

	except (exceptions.SubsonicError, subsonic.SessionError):
		pass


def process_share_hist(share_history: list) -> list:
	"""
	Processes a list of share history records and updates the display name for each record.

	Args:
		share_history (list): A list of dictionaries, where each dictionary represents
			a share history record. Each record must contain 'user_id' and 'name' keys.

	Returns:
		list: A list of dictionaries with updated 'display_name' keys.
			If 'user_id' is None, 'display_name' is set to 'name'.
			If 'user_id' is not None, 'display_name' is set to the display name of the user.
			If the user does not exist, 'display_name' is set to 'name'.
	"""
	share_hist = []
	for hist in share_history:
		if hist['user_id'] is None:
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
	"""
	Tokenizes the input text into a list of unique keywords.

	Args:
		text (str): The input text to be tokenized.

	Returns:
		list[str]: A list of unique keywords extracted from the input text.
	"""
	keywords = _P['nonwd'].sub(' ', _P['tag'].sub(' ', text.replace('\'', ''))).lower().split()
	return list(set(
		i for i in keywords if len(i) > 2
	))


def build_keywords(book_data: dict) -> list[str]:
	"""
	Extracts and builds a list of unique keywords from the given book data.

	This function processes specific fields ('title', 'subtitle', 'description', 'authors')
	from the provided book data dictionary. It tokenizes the content of these fields into
	keywords and returns a sorted list of unique keywords.

	Args:
		book_data (dict): A dictionary containing book information. Expected keys are
						  'title', 'subtitle', 'description', and 'authors'. The value
						  for 'authors' can be a list of strings, while the other fields
						  are expected to be strings.

	Returns:
		list[str]: A sorted list of unique keywords extracted from the specified fields
				   in the book data.
	"""
	keywords = []
	for field in ['title', 'subtitle', 'description', 'authors']:
		field_data = book_data.get(field)
		if field_data is None:
			continue
		if isinstance(field_data, list):
			for i in field_data:
				keywords += keyword_tokenize(i)
		else:
			keywords += keyword_tokenize(field_data)

	return sorted(list(set(keywords)))


def subsonic_init() -> subsonic.SubsonicClient:
	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')
	return init_subsonic(url, username, password)


def process_book_tag(book_data: dict) -> dict:
	"""
	Processes and enriches book data with additional information.

	Args:
		book_data (dict): A dictionary containing book information.

	Returns:
		dict: The enriched book data dictionary.

	Raises:
		exceptions.UserDoesNotExistError: If the user does not exist.
		exceptions.BlobDoesNotExistError: If the blob does not exist.
	"""
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

	try:
		client = get_subsonic()
		if client is None:
			client = subsonic_init()

		# If this title is not in the album cache, then fetch more
		global subsonic_albums_complete, subsonic_albums_page, subsonic_albums
		while not subsonic_albums_complete and (
			len(subsonic_albums) == 0 or
			subsonic_albums[-1].title <= book_data['title']
		):
			albums = client.albums('Audiobooks', subsonic_albums_page, 40)
			subsonic_albums += albums

			subsonic_albums_page += 1
			if len(albums) < 40:
				subsonic_albums_complete = True

		# Check if any album is a close enough match to this book title
		for album in subsonic_albums:
			album_title = re.sub(
				r'\(.*\)|[' + re.escape(string.punctuation) + r']',
				'',
				album.title
			).strip().lower()
			title: str = book_data['title'].strip().lower()
			subtitle: str = (book_data['subtitle'] if book_data['subtitle'] else '').strip().lower()

			if album_title in (
				title,
				f'{title} {subtitle}',
			):
				book_data['audiobook'] = album.id
				break

	except (exceptions.SubsonicError, subsonic.SessionError):
		pass

	book_data['has_description'] = len((book_data.get('description', '') or '').strip()) > 0

	return book_data


def get_book_tag(rfid: str, *, parse: bool = False) -> dict:
	"""
	Retrieve a book tag from the database using its RFID.

	Args:
		rfid (str): The RFID of the book tag to retrieve.
		parse (bool, optional): If True, the book data will be
			processed before returning. Defaults to False.

	Returns:
		dict: The book tag data. If `parse` is True, the data will be processed.

	Raises:
		BookTagDoesNotExistError: If no book tag with the given RFID is found in the database.
	"""
	book_data = db.find_one({'rfid': rfid})

	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	return process_book_tag(book_data) if parse else book_data


def get_book(id: str, *, parse: bool = False) -> dict:
	"""
	Retrieve a book from the database by its ID.

	Args:
		id (str): The ID of the book to retrieve.
		parse (bool, optional): If True, the book data will be
			processed before returning. Defaults to False.

	Returns:
		dict: The book data, either raw or processed based on the `parse` parameter.

	Raises:
		BookTagDoesNotExistError: If no book with the given ID is found in the database.
	"""
	book_data = db.find_one({'_id': ObjectId(id)})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(id)

	return process_book_tag(book_data) if parse else book_data


def next_out_of_date_book_rfid(before: datetime) -> str | None:
	"""
	Retrieve the RFID of the next book that is out of date.

	This function queries the database for a book whose 'lastSync' field is 
	earlier than the specified 'before' datetime. If such a book is found, 
	its RFID is returned. If no such book is found, None is returned.

	Args:
		before (datetime): The cutoff datetime to find books that are out of date.

	Returns:
		str: The RFID of the next out-of-date book, or None if no such book is found.
	"""
	book_data = db.find_one({'lastSync': {'$lt': before}})
	if book_data is None:
		return None

	return book_data['rfid']


def refresh_book_data(rfid: str) -> None:
	"""
	Refreshes the book data in the database using the provided RFID.

	This function retrieves the book data from the database using the RFID,
	fetches updated book information from the Google Books API, and updates
	the database with the new information. If the book data does not exist
	in the database, it raises a BookTagDoesNotExistError.

	Args:
		rfid (str): The RFID of the book to refresh.

	Raises:
		BookTagDoesNotExistError: If the book data does not exist in the database.
	"""
	book_data = db.find_one({'rfid': rfid})

	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(rfid)

	google_book_data = google_books.get(id=book_data['bookId'])

	fields = [
		'title', 'subtitle', 'authors', 'publisher', 'publishedDate',
		'description', 'industryIdentifiers', 'pageCount',
		'categories', 'maturityRating', 'language', 'thumbnail',
	]
	updated: dict = {'lastSync': datetime.utcnow()}
	for i in fields:
		if i in book_data.get('noSyncFields', []):
			continue

		new_val = google_book_data.get(i)
		if new_val is not None and new_val != book_data[i]:
			updated[i] = new_val

	updated['keywords'] = build_keywords({**book_data, **updated})

	db.update_one({'rfid': rfid}, {'$set': updated})


def link_book_tag(owner: str, rfid: str, book_id: str) -> dict:
	"""
	Links a book tag to a book in the database.

	Args:
		owner (str): The username of the owner of the book.
		rfid (str): The RFID tag to be linked to the book.
		book_id (str): The ID of the book to be linked.

	Returns:
		dict: A dictionary containing the book data after linking the tag.

	Raises:
		BookTagExistsError: If the RFID tag is already linked to a book.
	"""
	if db.find_one({'rfid': rfid}):
		raise exceptions.BookTagExistsError(rfid)

	google_book_data = google_books.get(id=book_id)
	del google_book_data['id']

	user_data = caller_info_strict()
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
	fields = [
		'title', 'subtitle', 'authors', 'publisher', 'publishedDate',
		'description', 'pageCount', 'categories', 'maturityRating',
		'language', 'thumbnail',
	]
	for i in fields:
		book_data[i] = google_book_data.get(i)

	book_data['keywords'] = build_keywords(book_data)

	db.insert_one(book_data)

	book_data['owner'] = user_data
	book_data['shareHistory'] = process_share_hist(book_data['shareHistory'])

	return book_data


def create_book(owner: str, data: dict) -> dict:
	"""
	Creates a new book entry in the database.

	Args:
		owner (str): The username of the book owner.
		data (dict): A dictionary containing book information. Expected keys are:
			- 'rfid': The RFID of the book.
			- 'title': The title of the book.
			- 'subtitle': The subtitle of the book.
			- 'authors': A list of authors of the book.
			- 'publisher': The publisher of the book.
			- 'publishedDate': The published date of the book.
			- 'description': A description of the book.
			- 'pageCount': The number of pages in the book.
			- 'thumbnail': A URL to the thumbnail image of the book.
			- 'isbn' (optional): The ISBN of the book.

	Returns:
		dict: A dictionary containing the created book data.
	"""
	user_data = caller_info_strict()
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
		'description': (
			None if data['description'] is None else
			markdown.markdown(data['description'])
		),
		'pageCount': data['pageCount'],
		'categories': [],
		'maturityRating': 'NOT_MATURE',
		'language': 'en',
		'thumbnail': (
			data['thumbnail'].replace('http://', 'https://')
			if data['thumbnail'] else data['thumbnail']
		),
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
	"""
	Unlink a book tag from the database using its RFID.

	This function searches for a book in the database using the provided RFID.
	If the book is found, it deletes the book entry from the database and removes
	any reference to its thumbnail if it is a locally hosted blob.

	Args:
		rfid (str): The RFID of the book to be unlinked.

	Returns:
		dict: The data of the book that was unlinked.

	Raises:
		BookTagDoesNotExistError: If no book with the given RFID is found in the database.
	"""
	book_data = db.find_one({'rfid': rfid})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(rfid)

	db.delete_one({'rfid': rfid})

	# Remove reference to this thumbnail if it uses a locally hosted blob.
	if book_data['thumbnail']:
		blob.remove_reference(book_data['thumbnail'])

	return book_data


def relink_book_tag(id: str, rfid: str) -> dict:
	"""
	Change the RFID of a book tag to a new one.

	Args:
		id (str): The ID of the book.
		rfid (str): The new RFID for the book tag.

	Returns:
		dict: The updated book tag information.

	Raises:
		exceptions.BookTagDoesNotExistError: If the book with the given ID does not exist.
		exceptions.BookTagExistsError: If the new RFID already exists in the database.
	"""

	book_data = db.find_one({'_id': ObjectId(id)})
	if not book_data:
		raise exceptions.BookTagDoesNotExistError(id)

	if db.find_one({'rfid': rfid}):
		raise exceptions.BookTagExistsError(rfid)

	db.update_one({'_id': ObjectId(id)}, {'$set': {'rfid': rfid}})
	book_data['rfid'] = rfid

	return book_data


def norm_query(query: dict, ownerq: dict | None) -> dict:
	"""
	Normalize a query by combining it with an owner query if provided.

	Args:
		query (dict): The initial query dictionary.
		ownerq (dict | None): An optional owner query dictionary.

	Returns:
		dict: The combined query dictionary if both query and ownerq are provided,
			  otherwise returns the non-None query dictionary.
	"""
	if ownerq is not None:
		if query:
			return {'$and': [query, ownerq]}
		return ownerq
	return query


def build_book_query(filter: BookSearchFilter, sort: list) -> tuple[list[dict] | None, dict]:
	"""
	Builds a MongoDB query and aggregation pipeline based on the provided filter and sort criteria.

	Args:
		filter (BookSearchFilter): A dictionary containing search filters for books.
			- owner (str or list): The owner(s) of the book.
			- author (str): The author of the book.
			- genre (str): The genre of the book.
			- shared (bool): Whether the book is shared.
			- title (str): The title or ISBN of the book.
		sort (list, optional): A list of tuples specifying the sort order. Defaults to [].

	Returns:
		tuple: A tuple containing:
			- aggregate (list or None): The aggregation pipeline if applicable, otherwise None.
			- query (dict): The MongoDB query dictionary.
	"""
	query = {}
	aggregate: list[dict] | None = None

	owner: list[str] | str | None = filter.get('owner')
	ownerq = None
	if owner is not None:
		if isinstance(owner, str):
			user_data = users.get_user_data(owner)
			query['owner'] = user_data['_id']
		elif isinstance(owner, list) and len(owner) > 0:
			ownerq = {'$or': [{'owner': i} for i in owner]}

	if filter.get('author') is not None:
		query['authors'] = {'$regex': filter.get('author'), '$options': 'i'}

	if filter.get('genre') is not None:
		query['categories'] = {'$regex': filter.get('genre'), '$options': 'i'}

	if filter.get('shared') is not None:
		query['shared'] = filter.get('shared')

	title = filter.get('title')
	if title is not None:
		isbn = title.strip().replace('-', '')
		if re.match(r'^\d{9,13}$', isbn):
			query['industryIdentifiers.identifier'] = isbn
			query = norm_query(query, ownerq)
		else:
			keywords = keyword_tokenize(title)
			query['keywords'] = {'$in': keywords}
			query['score'] = {'$gt': (len(keywords) + 1) // 2 if len(keywords) > 1 else 0}
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
				{'$sort': {'score': -1, **{i[0]: i[1] for i in sort}}}
			]
	else:
		query = norm_query(query, ownerq)

	return aggregate, query


def get_books(filter: BookSearchFilter, start: int, count: int, sorting: Sorting) -> list:
	"""
	Retrieve a list of books from the database based on
	the given filter, pagination, and sorting criteria.

	Args:
		filter (BookSearchFilter): The filter criteria to apply to the book search.
		start (int): The starting index for pagination.
		count (int): The number of books to retrieve.
		sorting (Sorting): The sorting criteria, including
			fields to sort by and order (ascending/descending).

	Returns:
		list: A list of books that match the filter criteria, sorted and paginated as specified.
	"""
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

	selection: Cursor | None = None

	if aggregate:
		aggr_filter = [{'$facet': {'results': [{'$skip': start}, {'$limit': count}]}}]
		for i in db.aggregate(aggregate + aggr_filter):
			selection = i['results']
	else:
		selection = db.find(query, sort=sort).limit(count).skip(start)

	if selection is None:
		return books

	for i in selection:
		i = process_book_tag(i.get('results', i))
		books += [i]

	return books


def count_books(filter: BookSearchFilter) -> int:
	"""
	Count the number of books in the database based on the provided filter.

	Args:
		filter (BookSearchFilter): The filter criteria to search for books.

	Returns:
		int: The count of books that match the filter criteria.
			Returns 0 if the user does not exist or no books match the criteria.

	Raises:
		exceptions.UserDoesNotExistError: If the user specified in the filter does not exist.
	"""
	try:
		aggregate, query = build_book_query(filter, [])
	except exceptions.UserDoesNotExistError:
		return 0

	if aggregate:
		aggr_filter = [{'$facet': {'count': [{'$count': 'count'}]}}]
		for i in db.aggregate(aggregate + aggr_filter):
			ct = i['count']
			return ct[0]['count'] if len(ct) else 0
	else:
		return db.count_documents(query)

	# Should never reach here, but just in case.
	return 0


def share_book_with_user(book_id: str, username: str) -> dict:
	"""
	Marke a book as shared (with a user), updating the book's share history.

	Args:
		book_id (str): The ID of the book to be shared.
		username (str): The username of the user with whom the book is being shared.

	Returns:
		dict: The book data after the share operation.

	Raises:
		exceptions.BookTagDoesNotExistError: If the book with the given ID does not exist.
	"""

	book_obj_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_obj_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	user_data = users.get_user_data(username)

	if len(book_data['shareHistory']):
		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_obj_id}, {'$set': updates})
	db.update_one({'_id': book_obj_id}, {'$push': {'shareHistory': {
		'user_id': user_data['_id'],
		'name': username,
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data


def share_book_with_non_user(book_id: str, name: str) -> dict:
	"""
	Share a book with a non-user by updating the book's share history.

	Args:
		book_id (str): The ID of the book to be shared.
		name (str): The name of the non-user with whom the book is being shared.

	Returns:
		dict: The book data after the share operation.

	Raises:
		exceptions.BookTagDoesNotExistError: If the book with the given ID does not exist.
	"""
	book_obj_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_obj_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if len(book_data['shareHistory']):
		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_obj_id}, {'$set': updates})
	db.update_one({'_id': book_obj_id}, {'$push': {'shareHistory': {
		'user_id': None,
		'name': name,
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data


def borrow_book(book_id: str, user_data: dict) -> dict:
	"""
	Allows a user to borrow a book by updating the book's share history and status.

	Args:
		book_id (str): The ID of the book to be borrowed.
		user_data (dict): A dictionary containing user information, including:
			- '_id': The user's unique identifier.
			- 'username': The user's name.

	Returns:
		dict: The data of the book being borrowed.

	Raises:
		exceptions.BookTagDoesNotExistError: If the book with the given ID does not exist.
		exceptions.BookCannotBeShared: If the book is currently being borrowed by another user.
	"""
	book_obj_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_obj_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if len(book_data['shareHistory']):
		# If book is currently shared with a user OTHER THAN
		# the one requesting to borrow, Throw an exception.
		# In that case, someone needs to declare that it is
		# no longer being borrowed before it can be borrowed again.
		last_share = book_data['shareHistory'][-1]
		if last_share['stop'] is None and last_share['user_id'] != user_data['_id']:
			raise exceptions.BookCannotBeShared(
				f'This book is already being borrowed by {last_share["name"]}.'
			)

		last_share = len(book_data['shareHistory']) - 1
		updates = {'shared': True, f'shareHistory.{last_share}.stop': datetime.utcnow()}
	else:
		updates = {'shared': True}

	db.update_one({'_id': book_obj_id}, {'$set': updates})
	db.update_one({'_id': book_obj_id}, {'$push': {'shareHistory': {
		'user_id': user_data['_id'],
		'name': user_data['username'],
		'start': datetime.utcnow(),
		'stop': None,
	}}})

	return book_data


def return_book(book_id: str, user_data: dict) -> dict:
	"""
	Return a borrowed book to the library.

	Args:
		book_id (str): The ID of the book to be returned.
		user_data (dict): The data of the user returning the book, containing at least the user's ID.

	Returns:
		dict: The data of the book being returned.

	Raises:
		BookTagDoesNotExistError: If the book with the given ID does not exist.
		BookCannotBeShared: If the book is not currently shared or if the user did not borrow the book.
	"""
	book_obj_id = ObjectId(book_id)
	book_data = db.find_one({'_id': book_obj_id})
	if book_data is None:
		raise exceptions.BookTagDoesNotExistError(book_id)

	if not book_data['shared']:
		raise exceptions.BookCannotBeShared('Nobody is borrowing this book.')

	last_share = len(book_data['shareHistory']) - 1
	if (
		book_data['shareHistory'][-1]['user_id'] != user_data['_id']
		and book_data['owner'] != user_data['_id']
	):
		raise exceptions.BookCannotBeShared('You did not borrow this book.')

	db.update_one({'_id': book_obj_id}, {'$set': {
		'shared': False, f'shareHistory.{last_share}.stop': datetime.utcnow()
	}})
	return book_data


def set_book_owner(id: str, username: str) -> dict:
	"""
	Updates the owner of a book and records the ownership history.

	Args:
		id (str): The unique identifier of the book.
		username (str): The username of the new owner.

	Returns:
		dict: The updated book data including the new owner and ownership history.
	"""
	book_data = get_book(id, parse=True)
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
	"""
	Edit the details of a book in the database.

	Args:
		id (str): The unique identifier of the book to be edited.
		new_data (dict): A dictionary containing the new data for the book.

	Returns:
		dict: The updated book data.

	This function retrieves the current data of the book using its ID,
	compares it with the new data provided, and updates the fields that have changed.
	It also updates the 'noSyncFields' to include the changed fields.
	Finally, it updates the book data in the database and returns the updated book data.
	"""
	book_data = get_book(id, parse=True)

	changed_fields = {}
	for i in new_data:
		if i in book_data and new_data[i] != book_data[i]:
			changed_fields[i] = new_data[i]
			book_data[i] = new_data[i]

	changed_fields['noSyncFields'] = list(set(
		book_data.get('noSyncFields', []) + [i for i in changed_fields]
	))
	book_data['noSyncFields'] = changed_fields['noSyncFields']

	db.update_one({'_id': ObjectId(id)}, {'$set': changed_fields})

	return book_data


def count_all_user_books(filter_users: list | None = None) -> list:
	"""
	Count the number of books owned by each user.

	This function aggregates the total number of books for each user in the database.
	It can also filter the results to include only specific users if a list of user IDs is provided.

	Args:
		filter_users (list | None): A list of user IDs to filter the results.
			If None, all users are included.

	Returns:
		list: A list of dictionaries, each containing the 'owner' information
			(username and display name) and the 'count' of books owned by that user.
	"""
	aggregate = db.aggregate([
		{'$group': {'_id': '$owner', 'count': {'$sum': 1}}}
	])

	result = []

	for i in aggregate:
		# Allow user group filtering
		if filter_users is not None and i['_id'] not in filter_users:
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
			# Just ignore users that no longer exist.
			pass

	return result


def append_ebook(book_id: str, ebook_url: str) -> dict:
	"""
	Append an ebook to the book's ebook list and update the database.

	Args:
		book_id (str): The unique identifier of the book.
		ebook_url (str): The URL of the ebook to be appended.

	Returns:
		dict: The updated book data.

	Raises:
		exceptions.BlobDoesNotExistError: If the ebook URL does not exist in the blob storage.
	"""
	book_data = get_book(book_id)

	ext = 'unk'

	try:
		blob_data = blob.get_blob_data(ebook_url)
		blob.add_reference(ebook_url)  # If using blob id instead of file url, update the reference count.
		ext = blob_data['ext'].strip('.')
	except exceptions.BlobDoesNotExistError:
		pos = ebook_url.rfind('.')
		ext = ebook_url[pos + 1::] if pos > -1 else 'unk'

	book_data['ebooks'] += [{
		'url': ebook_url,
		'fileType': ext.lower(),
	}]

	db.update_one({'_id': ObjectId(book_id)}, {'$set': {'ebooks': book_data['ebooks']}})

	return book_data


def remove_ebook(book_id: str, index: int) -> dict:
	"""
	Remove an ebook from the book's ebook list and update the database.

	Args:
		book_id (str): The unique identifier of the book.
		index (int): The URL of the ebook to be appended.

	Returns:
		dict: The updated book data.

	Raises:
		exceptions.BookTagDoesNotExistError: If the book with the given ID does not exist.
	"""
	book_data = get_book(book_id)
	ebooks: list = book_data.get('ebooks', [])

	if index < 0 or index >= len(ebooks):
		return book_data

	ebook_url: str = ebooks.pop(index).get('url', '')

	try:
		blob.get_blob_data(ebook_url)
		blob.remove_reference(ebook_url)  # If using blob id instead of file url, update the reference count.
	except exceptions.BlobDoesNotExistError:
		pass

	db.update_one({'_id': ObjectId(book_id)}, {'$set': {'ebooks': ebooks}})
	book_data['ebooks'] = ebooks

	return book_data
