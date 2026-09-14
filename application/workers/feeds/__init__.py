"""Automatically fetch and update data feeds."""
import time
from datetime import datetime, timedelta

import praw

from application.db.notification import send
from application.db.settings import get_config

from .api import API
from .fetch_next_document import fetch_next_document
from .get_feeds import get_feeds

## The number of seconds to wait between API calls to avoid rate limiting
API_DELAY = 1


def fetch_feeds(**kwargs) -> None:
	"""
		Automatically fetch and update data feeds.

	Args:
		kwargs: The max number of time that this process should run.
	"""

	end_time = datetime.now() + timedelta(**kwargs) - timedelta(seconds=30)

	praw_ini_text = get_config('feed:reddit:praw.ini')
	reddit_username = get_config('feed:reddit:username')

	if not reddit_username or not praw_ini_text:
		# Currently, no other feeds are supported besides Reddit.
		return

	with open('praw.ini', 'w', encoding='utf8') as fp:
		fp.write(praw_ini_text)

	API.reddit = praw.Reddit(reddit_username, check_for_async=False)

	for feed in get_feeds():
		if datetime.now() >= end_time:
			break

		# pylint: disable=broad-except
		fetched_documents = 0
		try:
			while fetch_next_document(feed) and datetime.now() < end_time:
				# Keep fetching documents until there are no more new ones.
				fetched_documents += 1
				time.sleep(API_DELAY)
		except Exception as e:
			# We don't want one feed failure to kill the whole process.
			# Log it and move on.
			print(f'FEED FETCH ERROR: {e}', flush=True)

		try:
			if fetched_documents and feed['notify']:
				send(
					title=feed['name'],
					body=(
						f'{"A" if fetched_documents == 1 else fetched_documents}' +
						f' new post{"" if fetched_documents == 1 else "s"}' +
						f' {"has" if fetched_documents == 1 else "have"}' +
						' been added to your feed.'
					),
					username=feed['creator'],
					category='feed'
				)
		except Exception as e:
			# We don't want one failure to kill the whole process.
			# Log it and move on.
			print(f'FEED FETCH ERROR: {e}', flush=True)
