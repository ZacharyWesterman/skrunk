"""application.resolvers.query.integrations"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.settings import get_config
from application.integrations import (get_subsonic, init_subsonic, subsonic,
                                      system)

from . import query


def subsonic_init() -> subsonic.SubsonicClient:
	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')
	return init_subsonic(url, username, password)


# pylint: disable=redefined-outer-name
@query.field('searchSubsonic')
@perms.module('subsonic')
def resolve_search_subsonic(_, _info: GraphQLResolveInfo, query: str, start: int, count: int) -> dict:
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
	return {'__typename': 'SystemInfo', 'storage': system.disk_usage()}
