"""application.resolvers.query.integrations"""

from graphql.type import GraphQLResolveInfo
from application.integrations import subsonic, system
from application.exceptions import SubsonicError
from application.db.settings import get_config
from application.db import perms
from . import query

SUBSONIC: subsonic.SubsonicClient | None = None


def init_subsonic() -> subsonic.SubsonicClient:

	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')

	if not url or not username or not password:
		raise SubsonicError()

	return subsonic.SubsonicClient(url, username, password)


@query.field('searchSubsonic')
@perms.module('subsonic')
def resolve_search_subsonic(_, info: GraphQLResolveInfo, query: str, start: int, count: int) -> dict:
	global SUBSONIC
	if SUBSONIC is None:
		SUBSONIC = init_subsonic()

	try:
		res = SUBSONIC.search(query)

		return {
			'__typename': 'SubsonicSearch',
			'album': [
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
			],
		}
	except subsonic.SessionError as e:
		return {'__typename': 'SubsonicError', 'message': str(e)}


@query.field('subsonicAlbumTrackList')
@perms.module('subsonic')
def resolve_subsonic_album_track_list(_, info: GraphQLResolveInfo, id: str) -> list:
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
	except subsonic.SessionError as e:
		return []


@query.field('subsonicCoverArt')
@perms.module('subsonic')
def resolve_subsonic_cover_art(_, info: GraphQLResolveInfo, id: str) -> str:
	global SUBSONIC
	if SUBSONIC is None:
		SUBSONIC = init_subsonic()

	try:
		return SUBSONIC.cover_art(id)
	except subsonic.SessionError as e:
		return ''


@query.field('getSystemInfo')
@perms.require('admin')
def resolve_get_system_info(_, info: GraphQLResolveInfo) -> dict:
	return {'__typename': 'SystemInfo', 'storage': system.disk_usage()}
