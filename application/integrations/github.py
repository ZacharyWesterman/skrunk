__ALL__ = ['Repository', 'CurrentRepository']

import json
import requests
import subprocess
from .exceptions import RepoFetchFailed

class Repository:
	def __init__(self, owner, repo):
		self.url = f'https://api.github.com/repos/{owner}/{repo}'

	def issues(self) -> list:
		url = self.url + '/issues?state=open'
		res = requests.get(url)
		if res.status_code >= 200 and res.status_code < 300:
			return json.loads(res.text)
		else:
			raise RepoFetchFailed(self.url)

class CurrentRepository(Repository):
	def __init__(self):
		repo_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'])
		info = repo_url.decode().strip().split(':')[1].split('/')

		owner = info[0]
		repo = info[1][:-4]

		super().__init__(owner, repo)