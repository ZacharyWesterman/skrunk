import requests
import hashlib
import random
import json
import functools
import urllib

class SessionError(Exception):
	def __init__(self, message: str):
		super().__init__(f'Subsonic Error: {message}')

class Session:
	def __init__(self, host: str, username: str, password: str, *, client: str = 'serverclient', version: str = '1.15.0'):
		salt = '%32x' % random.randrange(16**32) #random 32 digit hex string

		# Note that the password you pass in depends on how the credentials are stored on the server side!
		# E.g. if it's stored in plaintext, pass in the plain text password
		# however, if the encoder is MD5, pass in the md5sum to this function, NOT the plaintext password!
		md5sum = hashlib.md5((password + salt).encode('utf-8')).hexdigest()

		self.rest_params = f'u={username}&t={md5sum}&s={salt}&c={client}&v={version}&f=json'
		self.connection_uri = host

	def query(self, action: str, parameters: dict = {}) -> dict:
		url = f'{self.connection_uri}/rest/{action}.view?{self.rest_params}'
		for p in parameters:
			if parameters[p] is not None:
				url += f'&{p}={urllib.parse.quote_plus(parameters[p])}'

		res = requests.get(url)

		if res.status_code >= 300 or res.status_code < 200:
			raise SessionError(f'Failed to connect to server (code {res.status_code})')

		data = json.loads(res.text)
		if data['subsonic-response']['status'] != 'ok':
			raise SessionError('')

		return data['subsonic-response']

	def ping(self) -> dict:
		return self.query('ping')

	@functools.cached_property
	def folders(self) -> dict:
		data = self.query('getMusicFolders')

		output = {}
		for i in data['musicFolders']['musicFolder']:
			output[i['id']] = i['name']

		return output

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

	def cover_art(self, album_id: str) -> str:
		return f'{self.connection_uri}/coverArt.view?size=160&id={album_id}'

