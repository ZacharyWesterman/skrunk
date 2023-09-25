from application.integrations import subsonic
from application.db.settings import get_config

def resolve_search_subsonic(_, info, query: str, start: int, count: int) -> list:
	url = get_config('subsonic:url')
	username = get_config('subsonic:username')
	password = get_config('subsonic:password')

	session = subsonic.Session(url, username, password)

	try:
		res = session.search(query)
		if 'album' in res:
			for i in res['album']:
				i['coverArt'] = session.cover_art(i['coverArt']) if 'coverArt' in i else ''

		return {
			'__typename': 'SubsonicSearch',
			'album': res.get('album', []),
		}
	except subsonic.SessionError as e:
		return { '__typename': 'SubsonicError', 'message': str(e) }
