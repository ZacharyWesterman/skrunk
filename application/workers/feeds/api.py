import praw


class API:
	"""
	API class that encapsulates a various API clients.

	Attributes:
		reddit (praw.Reddit): An instance of the PRAW Reddit client
			used to interact with the Reddit API.
	"""
	reddit: praw.Reddit
