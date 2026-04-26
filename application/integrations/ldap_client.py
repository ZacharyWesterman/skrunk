import base64
import hashlib
from threading import Thread
from typing import Generator, Iterable

import bcrypt
import ldap
import ldap.asyncsearch
from ldap.ldapobject import LDAPObject

SYNC_THREAD = None
CONNECTION: LDAPObject | None = None
LDAP_ADMIN_USER = 'admin'
LDAP_ADMIN_PASS = 'password'
LDAP_DOMAIN = 'nodomain'

# pylint: disable=no-member
# pylance: disable=reportAttributeAccessIssue


def init(connection_uri: str, *, username: str = 'admin', password: str, domain: str = 'nodomain') -> None:
	"""
	Initialize the LDAP connection
	"""

	global CONNECTION, LDAP_ADMIN_USER, LDAP_ADMIN_PASS, LDAP_DOMAIN
	try:
		CONNECTION = ldap.initialize(connection_uri)
	except ldap.LDAPError as e:  # pyright: ignore[reportAttributeAccessIssue]
		print(f'AD Error: {e}', flush=True)
		print(f'AD Settings: user={username}, domain={domain}', flush=True)

	LDAP_ADMIN_USER = username
	LDAP_ADMIN_PASS = password
	LDAP_DOMAIN = domain


def ldap_can_connect() -> bool:
	if CONNECTION is None:
		return False

	try:
		CONNECTION.simple_bind_s('', '')
	except ldap.SERVER_DOWN:  # pyright: ignore[reportAttributeAccessIssue]
		print('AD Server Down', flush=True)
		return False
	except ldap.INVALID_CREDENTIALS:  # pyright: ignore[reportAttributeAccessIssue]
		print('Invalid AD Credentials', flush=True)
		pass

	return True


def ldap_try_connection() -> bool:
	if CONNECTION is None:
		return False

	try:
		CONNECTION.simple_bind_s(f'cn={LDAP_ADMIN_USER},dc={LDAP_DOMAIN}', LDAP_ADMIN_PASS)
	except (ldap.SERVER_DOWN, ldap.INVALID_CREDENTIALS):  # pyright: ignore[reportAttributeAccessIssue]
		return False

	return True


def ldap_add_user(username: str, password: bytes) -> None:
	if CONNECTION is None or not ldap_try_connection():
		return

	entry = [
		('objectClass', [b"person"]),
		('cn', username.encode('utf-8')),
		('sn', username.encode('utf-8')),
		('userPassword', b'{CRYPT}' + password),
	]

	try:
		CONNECTION.add_s(f'cn={username},dc={LDAP_DOMAIN}', entry)
	except ldap.ALREADY_EXISTS:  # pyright: ignore[reportAttributeAccessIssue]
		pass


def ldap_update_username(username: str, new_username: str) -> None:
	if CONNECTION is None or not ldap_try_connection():
		return

	print('Updating LDAP', flush=True)

	entry = [
		(ldap.MOD_REPLACE, 'cn', [new_username.encode('utf-8')]),  # pyright: ignore[reportAttributeAccessIssue]
		(ldap.MOD_REPLACE, 'sn', [new_username.encode('utf-8')]),  # pyright: ignore[reportAttributeAccessIssue]
	]

	try:
		CONNECTION.modify_s(f'cn={username},dc={LDAP_DOMAIN}', entry)
	except ldap.NO_SUCH_OBJECT:  # pyright: ignore[reportAttributeAccessIssue]
		pass


def ldap_update_password(username: str, password: bytes) -> None:
	if CONNECTION is None or not ldap_try_connection():
		return

	entry = [
		(ldap.MOD_REPLACE, 'userPassword', [b'{CRYPT}' + password]),  # pyright: ignore[reportAttributeAccessIssue]
	]

	try:
		CONNECTION.modify_s(f'cn={username},dc={LDAP_DOMAIN}', entry)
	except ldap.NO_SUCH_OBJECT:  # pyright: ignore[reportAttributeAccessIssue]
		pass


def ldap_delete_user(username: str) -> None:
	if CONNECTION is None or not ldap_try_connection():
		return

	try:
		CONNECTION.delete_s(f'cn={username},dc={LDAP_DOMAIN}')
	except ldap.NO_SUCH_OBJECT:  # pyright: ignore[reportAttributeAccessIssue]
		pass


def ldap_list_users() -> list[dict[str, bytes]]:
	if CONNECTION is None or not ldap_try_connection():
		return []

	search = ldap.asyncsearch.List(CONNECTION)  # pyright: ignore[reportAttributeAccessIssue]
	search.startSearch(
		f'dc={LDAP_DOMAIN}',
		ldap.SCOPE_SUBTREE,  # pyright: ignore[reportAttributeAccessIssue]
		'(objectClass=person)'
	)

	try:
		partial = search.processResults()
	except ldap.SIZELIMIT_EXCEEDED:  # pyright: ignore[reportAttributeAccessIssue]
		print('WARN: AD: server-side size limit exceeded.', flush=True)
	else:
		if partial:
			print('WARN: AD: Only partial results received.', flush=True)

	return [
		{
			key: value[0] for (key, value) in entry[1][1].items()
		}
		for entry in search.allResults
	]


def ldap_import_users(user_list: Iterable) -> None:

	# Delete any existing users.
	for user in ldap_list_users():
		ldap_delete_user(user.get('cn', b'').decode('utf-8'))

	# Import the actual list of users.
	for user in user_list:
		ldap_add_user(**user)

	print('Finished syncing users to the LDAP server.', flush=True)


def sync_users(user_list: Iterable) -> bool:
	# Try to connect to ldap server first
	if not ldap_can_connect():
		return False

	global SYNC_THREAD
	SYNC_THREAD = Thread(target=ldap_import_users, args=(user_list,))
	SYNC_THREAD.start()

	return True

# pylint: enable=no-member
