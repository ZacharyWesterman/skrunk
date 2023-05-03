__all__ = ['query']

import requests
import json

from . import exceptions

_ENABLED = True
try:
	with open('data/secrets.json', 'r') as fp:
		API_KEY = json.load(fp).get('google_books')
		if API_KEY is None:
			_ENABLED = False
except FileNotFoundError:
	_ENABLED = False

if not _ENABLED:
	def red(text):
		return f'\033[91m{text}\033[0m'

	def gray(text):
		return f'\033[90m{text}\033[0m'

	print( red('   WARNING: No google_books API key found in data/secrets.json!'))
	print(gray('   Google Books integration will be disabled.'))

def query(*, title: str = '', author: str = '') -> list:
	if not _ENABLED:
		return []

	query_fields = []

	t = title.replace(':', '').strip().replace(' ', '+')
	a = author.replace(':', '').strip().replace(' ', '+')

	if len(t):
		query_fields += ['intitle:' + t] if len(a) else [t]
	if len(a):
		query_fields += ['inauthor:"' + a + '"']

	text_query = '+'.join(query_fields)
	response_fields = 'items(id,volumeInfo(authors,title,subtitle,description,industryIdentifiers,pageCount,categories,maturityRating,language,publisher,publishedDate,imageLinks))'

	url = f'https://www.googleapis.com/books/v1/volumes?q={text_query}&key={API_KEY}&fields={response_fields}&orderBy=relevance&maxResults=20'
	response = requests.get(url)
	if response.status_code != 200:
		raise exceptions.ApiFailedError(f'Google Books API call failed with status code {response.status_code}: {response.text}')

	books = []
	for i in json.loads(response.text).get('items', []):
		book = i['volumeInfo']
		book['id'] = i['id']
		book['authors'] = book.get('authors', [])
		book['thumbnail'] = book.get('imageLinks', {'thumbnail':None}).get('thumbnail')
		if book.get('title') is None:
			book['title'] = ''
		books += [book]

	return books

def get(*, id: str) -> dict:
	response_fields = 'id,volumeInfo(authors,title,subtitle,description,industryIdentifiers,pageCount,categories,maturityRating,language,publisher,publishedDate,imageLinks)'

	url = f'https://www.googleapis.com/books/v1/volumes/{id}?key={API_KEY}&fields={response_fields}'
	response = requests.get(url)
	if response.status_code != 200:
		raise exceptions.ApiFailedError(f'Google Books API call failed with status code {response.status_code}: {response.text}')

	book = json.loads(response.text)['volumeInfo']
	book['id'] = id
	book['authors'] = book.get('authors', [])
	book['thumbnail'] = book.get('imageLinks', {'thumbnail':None}).get('thumbnail')
	if book.get('title') is None:
		book['title'] = ''
	return book
