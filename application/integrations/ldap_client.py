from threading import Thread
from typing import Iterable

import ldap
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
		# ('uid', username.encode('utf-8')),
		('cn', username.encode('utf-8')),
		('sn', username.encode('utf-8')),
		('userPassword', password),
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
		('cn', new_username.encode('utf-8')),
		('sn', new_username.encode('utf-8')),
	]

	CONNECTION.modify_s(f'cn={username},dc={LDAP_DOMAIN}', entry)


def ldap_update_password(username: str, password: bytes) -> None:
	if CONNECTION is None or not ldap_try_connection():
		return

	entry = [
		('userPassword', password),
	]

	CONNECTION.modify_s(f'cn={username},dc={LDAP_DOMAIN}', entry)


def ldap_import_users(user_list: Iterable) -> None:

	for user in user_list:
		ldap_add_user(**user)

	print('Finished syncing users to the LDAP server.', flush=True)


def sync_users(user_list: Iterable) -> bool:
	print('Sync users...', flush=True)

	# Try to connect to ldap server first
	if not ldap_can_connect():
		return False

	print('User sync starting', flush=True)

	global SYNC_THREAD
	SYNC_THREAD = Thread(target=ldap_import_users, args=(user_list,))
	SYNC_THREAD.start()

	return True

# pylint: enable=no-member
