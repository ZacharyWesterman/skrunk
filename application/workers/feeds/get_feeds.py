"""Fetch a list of data feeds."""

from typing import Generator

from application.db import datafeed
from application.types import Feed


def get_feeds() -> Generator[Feed, None, None]:
	"""
	Retrieves active feeds from the given API session in batches.

	Yields:
		Feed: An active feed object.
	"""
	total = datafeed.count_feeds()
	feed_batch_size = 20

	for i in range(0, total, feed_batch_size):
		feed_list = datafeed.get_feeds(i, feed_batch_size)
		yield from (Feed(**i) for i in feed_list if not i['inactive'])
