"""application.resolvers.query.integrations"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.settings import get_config
from application.exceptions import SubsonicError
from application.integrations import subsonic, system

from . import query

SUBSONIC: subsonic.SubsonicClient | None = None


def init_subsonic() -> subsonic.SubsonicClient:

	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')

	if not url or not username or not password:
		raise SubsonicError()

	return subsonic.SubsonicClient(url, username, password)


# pylint: disable=redefined-outer-name
@query.field('searchSubsonic')
@perms.module('subsonic')
def resolve_search_subsonic(_, _info: GraphQLResolveInfo, query: str, start: int, count: int) -> dict:
	global SUBSONIC
	if SUBSONIC is None:
		SUBSONIC = init_subsonic()

	try:
		res = SUBSONIC.search(query)

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
	global SUBSONIC
	if SUBSONIC is None:
		SUBSONIC = init_subsonic()

	try:
		return [
			{
				'id': i.id,
				'title': i.title,
				'duration': i.duration or -1,
			} for i in SUBSONIC.album_songs(id)
		]
	except subsonic.SessionError:
		return []


@query.field('subsonicCoverArt')
@perms.module('subsonic')
def resolve_subsonic_cover_art(_, _info: GraphQLResolveInfo, id: str) -> str:
	global SUBSONIC
	if SUBSONIC is None:
		SUBSONIC = init_subsonic()

	try:
		return SUBSONIC.cover_art(id)
	except subsonic.SessionError:
		return ''


@query.field('getSystemInfo')
@perms.require('admin')
def resolve_get_system_info(_, _info: GraphQLResolveInfo) -> dict:
	return {'__typename': 'SystemInfo', 'storage': system.disk_usage()}
