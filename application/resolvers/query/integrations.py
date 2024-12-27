from application.integrations import subsonic, system
from application.db.settings import get_config
from application.db import perms
from . import query

SUBSONIC = None


@query.field('searchSubsonic')
@perms.module('subsonic')
def resolve_search_subsonic(_, info, query: str, start: int, count: int) -> list:
	global SUBSONIC

	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')

	if SUBSONIC is None:
		SUBSONIC = subsonic.SubsonicClient(url, username, password)

	try:
		res = SUBSONIC.search(query)

		return {
			'__typename': 'SubsonicSearch',
			'album': [
				{
					'id': i.id,
					'name': i.title,
					'coverArt': i.cover,
					'tracks': [
						{
							'id': a.id,
							'title': a.title,
							'duration': a.duration or -1,
						} for a in i.songs
					],
				} for i in res.albums or []
			],
		}
	except subsonic.SessionError as e:
		return {'__typename': 'SubsonicError', 'message': str(e)}


@query.field('getSystemInfo')
@perms.require('admin')
def resolve_get_system_info(_, info) -> dict:
	return {'__typename': 'SystemInfo', 'storage': system.disk_usage()}
