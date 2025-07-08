"""application.resolvers.mutation"""

from datetime import datetime
from typing import Callable

from ariadne import MutationType
from ariadne.types import Resolver

from application.db.perms import caller_info_strict


class MutationWrapper(MutationType):
	"""
	A wrapper for the MutationType class to keep track of when the last mutation was called.
	Attributes:
		last_mutation (dict | None): A dictionary containing the last mutation name, the username
		                             of the caller, and the timestamp of when it was called.
	"""

	def __init__(self):
		"""Initialize the MutationWrapper class."""
		super().__init__()

		## @var last_mutation: dict | None
		#  A dictionary containing the last mutation name, the username of the caller,
		#  and the timestamp of when it was called.
		self.last_mutation: dict | None = None

	def create_register_resolver(self, name: str) -> Callable[[Resolver], Resolver]:
		"""Decorator to register a mutation resolver and track the last mutation called."""

		parent_resolver = super().create_register_resolver(name)

		def wrapped_resolver(f: Resolver) -> Resolver:
			def func(*args, **kwargs):
				# Store the last mutation, who called it, and when it was called.
				# Do not store ANYTHING else, for privacy (and perhaps security?) reasons.
				self.last_mutation = {
					'request': name,
					'username': caller_info_strict().get('username'),
					'timestamp': datetime.now(),
				}
				return f(*args, **kwargs)
			return parent_resolver(func)

		return wrapped_resolver

	def get_last_mutation(self) -> dict | None:
		"""Get the last mutation name."""
		return self.last_mutation


## The MutationType object for the GraphQL schema.
mutation = MutationWrapper()

# pylint: disable=wrong-import-position
from . import apikeys  # nopep8
from . import blob  # nopep8
from . import book  # nopep8
from . import bugs  # nopep8
from . import datafeed  # nopep8
from . import documents  # nopep8
from . import inventory  # nopep8
from . import notification  # nopep8
from . import sessions  # nopep8
from . import settings  # nopep8
from . import users  # nopep8
from . import weather  # nopep8

# pylint: enable=wrong-import-position
