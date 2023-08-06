__all__ = ['query']

import requests
import json
import re

from . import exceptions

def query(*, title: str = '', author: str = '') -> list:
	query_fields = []

	t = title.replace(':', '').strip().replace(' ', '+')
	a = author.replace(':', '').strip().replace(' ', '+')

	if len(t):
		if len(a):
			query_fields += ['intitle:' + t]
		else:
			#Check if field is an ISBN number
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
	if response.status_code != 200:
		raise exceptions.ApiFailedError(f'Google Books API call failed with status code {response.status_code}: {response.text}')

	books = []
	for i in json.loads(response.text).get('items', []):
		book = i['volumeInfo']
		book['id'] = i['id']
		book['authors'] = book.get('authors', [])
		book['thumbnail'] = book.get('imageLinks', {'thumbnail':None}).get('thumbnail')
		if book.get('thumbnail') is not None:
			book['thumbnail'] = book['thumbnail'].replace('http://', 'https://')
		if book.get('title') is None:
			book['title'] = ''
		if book.get('categories') is None:
			book['categories'] = []
		books += [book]

	return books

def get(*, id: str) -> dict:
	response_fields = 'id,volumeInfo(authors,title,subtitle,description,industryIdentifiers,pageCount,categories,maturityRating,language,publisher,publishedDate,imageLinks)'

	url = f'https://www.googleapis.com/books/v1/volumes/{id}?fields={response_fields}'
	response = requests.get(url)
	if response.status_code != 200:
		raise exceptions.ApiFailedError(f'Google Books API call failed with status code {response.status_code}: {response.text}')

	book = json.loads(response.text)['volumeInfo']
	book['id'] = id
	book['authors'] = book.get('authors', [])
	book['thumbnail'] = book.get('imageLinks', {'thumbnail':None}).get('thumbnail')
	if book.get('thumbnail') is not None:
		book['thumbnail'] = book['thumbnail'].replace('http://', 'https://')
	if book.get('title') is None:
		book['title'] = ''
	if book.get('categories') is None:
			book['categories'] = []
	return book
