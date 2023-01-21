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

	if len(title):
		for i in title.replace(':', '').split(' '):
			query_fields += [f'intitle:{i}']
	if len(author):
		for i in author.replace(':', '').split(' '):
			query_fields += [f'inauthor:{i}']

	text_query = '+'.join(query_fields)

	response_fields = 'items(id,volumeInfo(authors,title,subtitle,description,industryIdentifiers,pageCount,categories,maturityRating,language,publisher,publishedDate,imageLinks))'

	url = f'https://www.googleapis.com/books/v1/volumes?q={text_query}&key={API_KEY}&fields={response_fields}'
	response = requests.get(url)
	if response.status_code != 200:
		raise exceptions.ApiFailedError(f'API call failed with status code {response.status_code}')

	return json.loads(response.text).get('items', [])
