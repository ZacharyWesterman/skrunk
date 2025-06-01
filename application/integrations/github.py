"""application.integrations.github"""

import json
import subprocess
from typing import Any

import cachetools.func
import requests

from .exceptions import RepoFetchFailed


@cachetools.func.ttl_cache()
def gh_request(url: str) -> Any:
	"""
	Sends a GET request to the specified GitHub API URL with authorization headers.

	This function reads the GitHub token from a local JSON file ('data/auth.json') and uses it to 
	set the 'Authorization' header for the request. If the request is successful (status code 2xx), 
	the response is returned as a dictionary. If the request fails, an error message is printed 
	and a RepoFetchFailed exception is raised.

	Args:
		url (str): The GitHub API URL to send the GET request to.

	Returns:
		dict: The JSON response from the GitHub API as a dictionary.

	Raises:
		RepoFetchFailed: If the request fails, this exception is raised with the URL and error message.
	"""
	headers = None
	try:
		with open('data/auth.json', 'r', encoding='utf8') as fp:
			headers = {
				'Authorization': 'Bearer ' + json.load(fp)['github'],
			}
	except OSError:
		pass

	res = requests.get(url, headers=headers, timeout=10)
	if res.status_code >= 200 and res.status_code < 300:
		return json.loads(res.text)
	else:
		print(res.text, flush=True)
		raise RepoFetchFailed(url, res.json().get('message'))


class Repository:
	"""
	A class to interact with a GitHub repository using the GitHub API.

	Attributes:
		url (str): The URL of the GitHub repository API endpoint.
	"""

	def __init__(self, owner: str, repo: str) -> None:
		"""
		Initializes the GitHub integration with the specified repository.

		Args:
			owner (str): The owner of the repository.
			repo (str): The name of the repository.
		"""

		## The URL of the GitHub repository API endpoint.
		self.url = f'https://api.github.com/repos/{owner}/{repo}'

	def issues(self, *, filter: str = 'state=open') -> list:
		"""
		Fetches a list of issues from the GitHub repository.

		Args:
			filter (str, optional): A query string to filter issues. Defaults to 'state=open'.

		Returns:
			list: A list of issues from the GitHub repository.
		"""
		return gh_request(self.url + '/issues?' + filter)

	def resolved_issues(self, since: str) -> list:
		"""
		Retrieve a list of resolved (closed) issues since a given date.

		Args:
			since (str): The date in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
				from which to retrieve closed issues.

		Returns:
			list: A list of issues that have been closed since the specified date.
		"""
		return self.issues(filter='state=closed&since=' + since)


class CurrentRepository(Repository):
	"""
	A class to represent the current GitHub repository.

	Inherits from:
		Repository

	Attributes:
		repo (str | None): The name of the repository. If None, it will be derived from the remote URL.
	"""

	def __init__(self, repo: str | None = None) -> None:
		"""
		Initialize the GitHub integration.

		This constructor retrieves the repository URL from the git configuration,
		extracts the owner and repository name, and initializes the parent class
		with these values. If the repository name is not provided, it is inferred
		from the URL.

		Args:
			repo (str | None): The name of the repository. If None, the repository
							   name is inferred from the git remote URL.

		Returns:
			None
		"""
		repo_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'])
		info = repo_url.decode().strip().split(':')[1].split('/')

		owner = info[0]
		if repo is None:
			repo = info[1][:-4]

		super().__init__(owner, repo)

	def issues_pending_resolution(self) -> list:
		"""
		Retrieves a list of issues that are pending resolution.

		This method gets the date and time of the last commit in the repository
		and uses it to fetch the list of issues that have been resolved since
		that commit.

		Returns:
			list: A list of issues that are pending resolution.
		"""
		last_commit = subprocess.check_output([
			'git', 'log', '-1', '--date=format:%Y-%m-%dT%T', '--format=%ad'
		]).decode().strip()
		return self.resolved_issues(last_commit)
