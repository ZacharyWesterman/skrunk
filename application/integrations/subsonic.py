__all__ = ['SessionError', 'Session']

import requests
import hashlib
import random
import json
import functools
import urllib
import base64
import asyncio
from aiohttp import ClientSession
from difflib import SequenceMatcher
import re

class SessionError(Exception):
	def __init__(self, message: str):
		super().__init__(f'Subsonic Error: {message}')

_P = re.compile('[\[\(][^\)]*[\[\)\]]')

class Session:
	def __init__(self, host: str, username: str, password: str, *, client: str = 'serverclient', version: str = '1.15.0'):
		salt = ('%32x' % random.randrange(16**32)).strip() #random 32 digit hex string

		# Note that the password you pass in depends on how the credentials are stored on the server side!
		# E.g. if it's stored in plaintext, pass in the plain text password
		# however, if the encoder is MD5, pass in the md5sum to this function, NOT the plaintext password!
		md5sum = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

		self.rest_params = f'u={username}&t={md5sum}&s={salt}&c={client}&v={version}&f=json'
		self.connection_uri = host

	def query(self, action: str, parameters: dict = {}, *, process: bool = True) -> dict:
		url = f'{self.connection_uri}/rest/{action}.view?{self.rest_params}'
		for p in parameters:
			if parameters[p] is not None:
				url += f'&{p}={urllib.parse.quote_plus(str(parameters[p]))}'

		res = requests.get(url)

		if res.status_code >= 300 or res.status_code < 200:
			raise SessionError(f'Failed to connect to server (code {res.status_code})')

		if not process:
			return res.content

		data = json.loads(res.text)
		if data['subsonic-response']['status'] != 'ok':
			raise SessionError(data['subsonic-response']['error']['message'])

		return data['subsonic-response']

	def ping(self) -> dict:
		return self.query('ping')

	@functools.cache
	def search(self, text: str, *, artist_count: int|None = None, artist_offset: int|None = None, album_count: int|None = None, album_offset: int|None = None, song_count: int|None = None, song_offset: int|None = None, music_folder_id: int|None = None) -> list:
		data = self.query('search2', {
			'query': text,
			'artistCount': artist_count,
			'artistOffset': artist_offset,
			'albumCount': album_count,
			'albumOffset': album_offset,
			'songCount': song_count,
			'songOffset': song_offset,
			'musicFolderId': music_folder_id,
		})
		return data['searchResult2']

	def cover_art_url(self, album_id: str) -> str:
		return f'{self.connection_uri}/coverArt.view?size=160&id={album_id}&{self.rest_params}'

	@functools.cache
	async def cover_art(self, album_id: str) -> str:
		url = f'{self.connection_uri}/rest/getCoverArt.view?{self.rest_params}&id={album_id}&size=160'

		async with ClientSession() as session, session.get(url) as result:
			res = await result.read()

			return album_id, base64.b64encode(res).decode()

	def get_all_cover_art(self, album_ids: list) -> list:

		#Async helper func to get all album covers for the given id list
		async def multi_albums(self, album_ids: list) -> list:
			tasks = [self.cover_art(i) for i in album_ids]
			result = await asyncio.gather(*tasks)
			return {id: data for id, data in result}

		return asyncio.run(multi_albums(self, album_ids))


	@functools.cached_property
	def folders(self) -> dict:
		data = self.query('getMusicFolders')

		output = {}
		for i in data['musicFolders']['musicFolder']:
			output[i['name']] = i['id']

		return output

	@functools.cached_property
	def license(self) -> str:
		return self.query('getLicense').get('license')

	@functools.cached_property
	def playlists(self) -> list:
		return self.query('getPlaylists').get('playlists', [])

	@functools.cache
	def playlist(self, name: str) -> dict:
		return self.query('getPlaylist').get('playlist')

	@functools.cache
	def albums(self, folder: str, page: int = 0) -> list:
		size = 100

		folder_id = self.folders.get(folder)
		if folder_id is None:
			raise SessionError(f'Folder "{folder}" does not exist')

		return self.query('getAlbumList', {
			'type': 'alphabeticalByName',
			'size': size,
			'offset': page * size,
			'musicFolderId': folder_id,
		}).get('albumList')

	@functools.cache
	def all_albums(self, folder: str) -> list[str]:
		global _P
		result = {}
		page = 0

		while True:
			res = self.albums(folder, page).get('album')
			if res is None:
				break

			for i in res:
				result[_P.sub('', i['title']).strip().lower()] = i['id']
			page += 1

		return result

	@functools.cache
	def album_in_folder(self, album: str, folder: str) -> bool:
		#Just a nearest match, not super exact
		for i in self.all_albums(folder):
			ratio = SequenceMatcher(None, album, i).ratio()
			if ratio >= 0.8:
				return True

		return False

	@functools.cache
	def get_album_id(self, album: str, folder: str) -> str:
		global _P

		all_albums = self.all_albums(folder)
		album = _P.sub('', album).strip().lower()

		for i in all_albums:
			if i.startswith(album) or album.startswith(i):
				return all_albums[i]

		return None
