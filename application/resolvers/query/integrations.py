"""application.resolvers.query.integrations"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.settings import get_config
from application.integrations import (get_subsonic, init_subsonic, subsonic,
                                      system)

from . import query


def subsonic_init() -> subsonic.SubsonicClient:
	"""
	Initializes and returns a SubsonicClient instance using configuration values.

	Fetches the Subsonic server URL, username, and password from the configuration,
	then initializes and returns a SubsonicClient object.

	Returns:
		subsonic.SubsonicClient: An initialized Subsonic client.

	Raises:
		KeyError: If any required configuration value is missing.
	"""
	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')
	return init_subsonic(url, username, password)


# pylint: disable=redefined-outer-name
@query.field('searchSubsonic')
@perms.module('subsonic')
def resolve_search_subsonic(_, _info: GraphQLResolveInfo, query: str, start: int, count: int) -> dict:
	"""
	Searches for albums in Subsonic using the provided query string and returns a paginated list of album information.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		query (str): The search query string.
		start (int): The starting index for pagination.
		count (int): The number of albums to return.

	Returns:
		dict: A dictionary containing either:
			- '__typename': 'SubsonicSearch' and 'album': a list of album dictionaries with metadata, or
			- '__typename': 'SubsonicError' and 'message': error details if the search fails.
	"""
	client = get_subsonic()
	if client is None:
		client = subsonic_init()

	try:
		res = client.search(query)

		albums = [
			{
				'id': i.id,
				'parent': i.parent,
				'isDir': i.isDir,
				'title': i.title,
				'album': i.album,
				'artist': i.artist,
				'year': i.year,
				'genre': i.genre,
				'coverArt': i.coverArt,
				'playCount': i.playCount,
				'created': i.created,
				'tracks': [],
			} for i in res.albums or []
		]

		if start >= len(albums):
			albums = []

		if count < 0 or start + count > len(albums):
			count = len(albums) - start

		return {
			'__typename': 'SubsonicSearch',
			'album': albums[start:start + count],
		}
	except subsonic.SessionError as e:
		return {'__typename': 'SubsonicError', 'message': str(e)}
# pylint: enable=redefined-outer-name


@query.field('subsonicAlbumTrackList')
@perms.module('subsonic')
def resolve_subsonic_album_track_list(_, _info: GraphQLResolveInfo, id: str) -> list:
	"""
	Fetches the list of tracks for a given Subsonic album ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the Subsonic album.

	Returns:
		list: A list of dictionaries, each containing the 'id', 'title', and 'duration' of a track.
			  If the album cannot be retrieved due to a session error, returns an empty list.
	"""
	client = get_subsonic()
	if client is None:
		client = subsonic_init()

	try:
		return [
			{
				'id': i.id,
				'title': i.title,
				'duration': i.duration or -1,
			} for i in client.album_songs(id)
		]
	except subsonic.SessionError:
		return []


@query.field('subsonicCoverArt')
@perms.module('subsonic')
def resolve_subsonic_cover_art(_, _info: GraphQLResolveInfo, id: str) -> str:
	"""
	Fetches the cover art URL for a given Subsonic media item ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The Subsonic media item ID for which to retrieve cover art.

	Returns:
		str: The URL of the cover art if available, otherwise an empty string.
	"""
	client = get_subsonic()
	if client is None:
		client = subsonic_init()

	try:
		return client.cover_art(id)
	except subsonic.SessionError:
		return ''


@query.field('getSystemInfo')
@perms.require('admin')
def resolve_get_system_info(_, _info: GraphQLResolveInfo) -> dict:
	"""
	Resolves the GraphQL query for retrieving system information.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict: A dictionary containing system information, including storage usage.
	"""
	return {'__typename': 'SystemInfo', 'storage': system.disk_usage()}
