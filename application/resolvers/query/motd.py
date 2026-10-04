"""application.resolvers.query.motd"""

from random import randint

from graphql.type import GraphQLResolveInfo

from application.db.motd import count_motd, get_nth_motd, list_motd
from application.types import Motd

from ..decorators import typed
from . import query


@query.field('countMotd')
def resolve_count_motd(_, _info: GraphQLResolveInfo) -> int:
	"""
	Resolver to count the total number of Messages of the Day.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		int: The total number of MOTD items.
	"""
	return count_motd()


@query.field('getRandomMotd')
@typed
def resolve_get_random_motd(_, _info: GraphQLResolveInfo) -> Motd | None:
	"""
	Resolver to get a random Message of the Day.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		Motd | None: A random MOTD, if any have been added.
	"""
	ct = count_motd()
	if ct == 0:
		return None

	index = randint(0, ct - 1)
	return get_nth_motd(index)


@query.field('getLatestMotd')
@typed
def resolve_get_latest_motd(_, _info: GraphQLResolveInfo) -> Motd | None:
	"""
	Resolver to get the most recent Message of the Day.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		Motd | None: The latest MOTD, if any have been added.
	"""
	ct = count_motd()
	if ct == 0:
		return None

	return get_nth_motd(ct - 1)


@query.field('listMotd')
def resolve_list_motd(_, _info: GraphQLResolveInfo, start: int, count: int) -> list[Motd]:
	"""
	Resolver to get a paginated list of Messages of the Day.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		start (int): The starting index for pagination.
		count (int): The number of items to retrieve.

	Returns:
		list[Motd]: A list of MOTD items.
	"""
	return list_motd(start, count)
