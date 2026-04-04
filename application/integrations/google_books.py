"""application.integrations.google_books"""

import functools
import json
import re
from datetime import datetime, timedelta

import requests

from application.db.settings import get_config

from . import exceptions

## Keep track of the last time that querying with the global API failed.
_global_query_failed: datetime | None = None


def _raw_query(url_query: str) -> str:
	"""
	Query the Google Books API.

	If querying without an API key fails due to an exceeded quota,
	fallback to querying with our API key (if we have one).
	Then if that fails, raise an error.

	Args:
		url_query (str): The raw query url, with all params except `key`.

	Returns:
		str: On success, the text response of the query.

	Raises:
		exceptions.ApiFailedError: If the Google Books API call fails.
	"""

	global _global_query_failed

	api_key = get_config('google_books')
	retry_with_api_key = True

	# If we already tried using the global API and the quota was exceeded, use our api key for a bit before trying it again.
	if api_key and _global_query_failed and (datetime.now() - _global_query_failed) < timedelta(minutes=30):
		url_query += f'&key={api_key}'
		retry_with_api_key = False

	response = requests.get(url_query, timeout=10)

	if retry_with_api_key and api_key and response.status_code == 429:
		# Quota exceeded for global, fallback to using API key.
		response = requests.get(f'{url_query}&key={api_key}', timeout=10)
		_global_query_failed = datetime.now()

	if response.status_code < 200 or response.status_code >= 300:
		raise exceptions.ApiFailedError(
			f'Google Books API call failed with status code {response.status_code}: {response.text}'
		)

	return response.text


@functools.cache
def query(*, title: str = '', author: str = '') -> list:
	"""
	Query the Google Books API for books matching the given title and/or author.

	Args:
		title (str): The title of the book to search for. Default is an empty string.
		author (str): The author of the book to search for. Default is an empty string.

	Returns:
		list: A list of dictionaries, each representing a book that matches the query.
			  Each dictionary contains the following keys:
			  - 'id': The unique identifier of the book.
			  - 'authors': A list of authors of the book.
			  - 'title': The title of the book.
			  - 'subtitle': The subtitle of the book (if available).
			  - 'description': A description of the book (if available).
			  - 'industryIdentifiers': A list of industry identifiers (e.g., ISBN) for the book.
			  - 'pageCount': The number of pages in the book.
			  - 'categories': A list of categories the book belongs to.
			  - 'maturityRating': The maturity rating of the book.
			  - 'language': The language the book is written in.
			  - 'publisher': The publisher of the book.
			  - 'publishedDate': The date the book was published.
			  - 'thumbnail': A URL to a thumbnail image of the book cover (if available).

	Raises:
		exceptions.ApiFailedError: If the Google Books API call fails.
	"""
	query_fields = []

	t = title.replace(':', '').strip().replace(' ', '+')
	a = author.replace(':', '').strip().replace(' ', '+')

	if len(t) > 0:
		if len(a) > 0:
			query_fields += ['intitle:' + t]
		else:
			# Check if field is an ISBN number
			isbn = t.replace('-', '')
			if re.match(r'^\d{9,13}$', isbn):
				query_fields += ['isbn:' + isbn]
			else:
				query_fields += [t]
	if len(a) > 0:
		query_fields += ['inauthor:"' + a + '"']

	text_query = '+'.join(query_fields)
	response_fields = (
		'items(id,volumeInfo(' +
		'authors,title,subtitle,description,industryIdentifiers,pageCount,' +
		'categories,maturityRating,language,publisher,publishedDate,imageLinks' +
		'))'
	)

	url = (
		'https://www.googleapis.com/books/v1/volumes' +
		f'?q={text_query}&fields={response_fields}&orderBy=relevance&maxResults=20'
	)
	response = json.loads(_raw_query(url))

	books = []
	for i in response.get('items', []):
		book = i['volumeInfo']
		book['id'] = i['id']
		book['authors'] = book.get('authors', [])
		book['thumbnail'] = book.get('imageLinks', {'thumbnail': None}).get('thumbnail')
		if book.get('thumbnail') is not None:
			book['thumbnail'] = book['thumbnail'].replace('http://', 'https://')
		if book.get('title') is None:
			book['title'] = ''
		if book.get('categories') is None:
			book['categories'] = []
		books += [book]

	return books


@functools.cache
def get(*, id: str) -> dict:
	"""
	Fetches book information from the Google Books API using the provided book ID.

	Args:
		id (str): The unique identifier for the book.

	Returns:
		dict: A dictionary containing book information such as authors, title, subtitle,
			  description, industry identifiers, page count, categories, maturity rating,
			  language, publisher, published date, and thumbnail URL.

	Raises:
		exceptions.ApiFailedError: If the Google Books API call fails.
	"""
	response_fields = (
		'id,volumeInfo(' +
		'authors,title,subtitle,description,industryIdentifiers,pageCount,' +
		'categories,maturityRating,language,publisher,publishedDate,imageLinks' +
		')'
	)

	url = f'https://www.googleapis.com/books/v1/volumes/{id}?fields={response_fields}'
	response = json.loads(_raw_query(url))

	book = response['volumeInfo']
	book['id'] = id
	book['authors'] = book.get('authors', [])
	book['thumbnail'] = book.get('imageLinks', {'thumbnail': None}).get('thumbnail')
	if book.get('thumbnail') is not None:
		book['thumbnail'] = book['thumbnail'].replace('http://', 'https://')
	if book.get('title') is None:
		book['title'] = ''
	if book.get('categories') is None:
		book['categories'] = []
	return book
