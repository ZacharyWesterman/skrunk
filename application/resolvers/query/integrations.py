from application.integrations import subsonic, system
from application.db.settings import get_config
from application.db import perms

def resolve_search_subsonic(_, info, query: str, start: int, count: int) -> list:
	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')

	session = subsonic.Session(url, username, password)

	try:
		res = session.search(query)
		if 'album' in res:
			album_ids = [i['coverArt'] for i in res['album'] if 'coverArt' in i]
			covers = session.get_all_cover_art(album_ids)

			for i in res['album']:
				if 'coverArt' in i:
					i['coverArt'] = covers[i['coverArt']]


		return {
			'__typename': 'SubsonicSearch',
			'album': res.get('album', []),
		}
	except subsonic.SessionError as e:
		return { '__typename': 'SubsonicError', 'message': str(e) }

@perms.require(['admin'])
def resolve_get_system_info(_, info) -> dict:
	return { '__typename': 'SystemInfo', 'storage': system.disk_usage() }
