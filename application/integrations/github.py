__ALL__ = ['Repository', 'CurrentRepository']

import json
import requests
import subprocess
from .exceptions import RepoFetchFailed
from datetime import datetime

class Repository:
	def __init__(self, owner, repo):
		self.url = f'https://api.github.com/repos/{owner}/{repo}'

	def issues(self, *, filter: str = 'state=open') -> list:
		url = self.url + '/issues?' + filter

		headers = None
		try:
			with open('data/auth.json', 'r') as fp:
				headers = {
					'Authorization': 'Bearer ' + json.load(fp)['github'],
				}
		except:
			pass

		res = requests.get(url, headers = headers)
		if res.status_code >= 200 and res.status_code < 300:
			return json.loads(res.text)
		else:
			print(res.text, flush=True)
			raise RepoFetchFailed(self.url)

	def resolved_issues(self, since: str) -> list:
		return self.issues(filter = 'state=closed&since=' + since)

class CurrentRepository(Repository):
	def __init__(self, repo: str|None = None):
		repo_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'])
		info = repo_url.decode().strip().split(':')[1].split('/')

		owner = info[0]
		if repo is None:
			repo = info[1][:-4]

		super().__init__(owner, repo)

	def issues_pending_resolution(self) -> list:
		last_commit = subprocess.check_output(['git', 'log', '-1', '--date=format:%Y-%m-%dT%T', '--format=%ad']).decode().strip()
		return self.resolved_issues(last_commit)
