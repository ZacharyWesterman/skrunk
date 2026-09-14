"""Attempt to fetch a new document for feeds."""

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from bson.objectid import ObjectId

from application.db.datafeed import (create_document, get_documents,
                                     update_document)
from application.exceptions import ClientError
from application.types import Feed

from .api import API


def fetch_next_document(feed: Feed) -> bool:
	"""
	Fetches the next document for a given feed and updates or creates a feed document accordingly.

	If a new document is created and notifications are enabled,
	it sends a notification to the feed creator.

	Any errors encountered during the process are logged.

	Args:
		feed (Feed): The feed dictionary containing feed metadata and configuration.

	Returns:
		bool: True if a new document was created or an existing document was updated,
			False otherwise.
	"""

	if feed['kind'] not in ['markdown_recursive']:
		print(f'FEED ERROR: Invalid feed kind "{feed["kind"]}" in feed {feed["id"]}!', flush=True)
		return False

	# Try to determine what website the feed URL links to so we can use the correct API
	hostname = urlparse(feed['url']).hostname
	if hostname is None:
		print(f'FEED ERROR: Feed {feed["id"]} has invalid URL "{feed["url"]}"', flush=True)
		return False

	addr = hostname.split('.')
	if len(addr) < 1:
		print(f'FEED ERROR: Feed {feed["id"]} has invalid hostname "{hostname}"', flush=True)
		return False

	feed_origin = ''

	if addr[-2::] == ['reddit', 'com']:
		# We know API is reddit.
		feed_origin = 'reddit'
	else:
		print(
			f'FEED ERROR: Could not determine origin for feed {feed["id"]} hostname "{hostname}"',
			flush=True
		)
		return False

	next_url = feed['url']
	document_body = None
	document_id = None

	# Assume feed kind is valid, we already validated it.
	if feed['kind'] == 'markdown_recursive':
		# Get most recent feed document, and search for (next)[...] to get the next document.
		documents = get_documents(
			feed['id'], 0, 1,
			{'_id': ObjectId(), 'fields': ['created'], 'descending': True}
		)

		if len(documents) > 0:
			doc = documents[0]
			next_url = doc['url']

			# Search for (next)[...]
			m = re.search(r'\[[Nn]ext[^\w\]]*\]\(([^)]*)\)', doc['body'])
			if m is not None:
				# If pattern was found, fetch the next URL
				next_url = m.group(1)
			else:
				document_body = doc['body']
				document_id = doc['id']

	# At this point, we have a next_url to fetch,
	# and we can create the document.
	document = {
		'feed': feed['id'],
		'author': None,
		'posted': None,
		'body': '[ERROR: NO BODY]',
		'title': None,
		'url': next_url,
	}

	if feed_origin == 'reddit':
		# print('FEED: Reaching out to Reddit API... ', end='', flush=True)
		post = API.reddit.submission(url=next_url)
		# print('Fetched post data.', flush=True)

		document['title'] = post.title
		document['body'] = post.selftext
		document['author'] = post.author.name
		document['posted'] = datetime.fromtimestamp(
			post.created_utc,
			timezone.utc
		).strftime('%Y-%m-%d %H:%M:%S')
	else:
		print(f'FEED ERROR: Cannot determine origin of feed {feed["id"]}', flush=True)
		return False

	try:
		if document_id:
			# We're just updating an existing document

			if document_body == document['body']:
				# Body hasn't changed, so do nothing.
				return False

			update_document(document_id, document['body'])
		else:
			# We're creating a new document
			create_document(**document)
	except ClientError as e:
		print(f'FEED ERROR: {e}')
		return False

	print(f'FEED: {"Updated" if document_id else "Fetched new"} document for feed {feed["id"]}')
	return True
