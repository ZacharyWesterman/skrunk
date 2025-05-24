"""application.integrations.google_books"""

__all__ = ['query']

import functools
import json
import re

import requests

from . import exceptions


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
		exceptions.ApiFailedError: If the Google Books API call fails with a status code outside the range 200-299.
	"""
	query_fields = []

	t = title.replace(':', '').strip().replace(' ', '+')
	a = author.replace(':', '').strip().replace(' ', '+')

	if len(t):
		if len(a):
			query_fields += ['intitle:' + t]
		else:
			# Check if field is an ISBN number
			isbn = t.replace('-', '')
			if re.match(r'^\d{9,13}$', isbn):
				query_fields += ['isbn:' + isbn]
			else:
				query_fields += [t]
	if len(a):
		query_fields += ['inauthor:"' + a + '"']

	text_query = '+'.join(query_fields)
	response_fields = 'items(id,volumeInfo(authors,title,subtitle,description,industryIdentifiers,pageCount,categories,maturityRating,language,publisher,publishedDate,imageLinks))'

	url = f'https://www.googleapis.com/books/v1/volumes?q={text_query}&fields={response_fields}&orderBy=relevance&maxResults=20'
	response = requests.get(url)
	if response.status_code < 200 or response.status_code >= 300:
		raise exceptions.ApiFailedError(f'Google Books API call failed with status code {response.status_code}: {response.text}')

	books = []
	for i in json.loads(response.text).get('items', []):
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
		exceptions.ApiFailedError: If the Google Books API call fails with a status code
								   outside the range of 200-299.
	"""
	response_fields = 'id,volumeInfo(authors,title,subtitle,description,industryIdentifiers,pageCount,categories,maturityRating,language,publisher,publishedDate,imageLinks)'

	url = f'https://www.googleapis.com/books/v1/volumes/{id}?fields={response_fields}'
	response = requests.get(url)
	if response.status_code < 200 or response.status_code >= 300:
		raise exceptions.ApiFailedError(f'Google Books API call failed with status code {response.status_code}: {response.text}')

	book = json.loads(response.text)['volumeInfo']
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
