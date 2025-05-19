"""application.db.settings"""

import json
from pymongo.collection import Collection
import application.exceptions as exceptions

## A pointer to the settings database collection.
db: Collection = None  # type: ignore[assignment]


def calculate_disabled_modules(disabled_modules: list[str]) -> list[str]:
	"""
	Calculate the complete list of disabled modules based on the provided list of disabled modules
	and the module configuration.

	Args:
		disabled_modules (list[str]): A list of module IDs that are initially disabled.

	Returns:
		list[str]: A list of module IDs that are disabled, including those that are 
				   indirectly disabled due to dependencies.
	"""

	module_config: dict | None = db.find_one({'name': 'modules'})
	if module_config is None:
		return []

	modules: list[str] = module_config.get('enabled', [])

	with open('site/config/modules.json', 'r') as fp:
		module_config = {i['id']: i for i in json.load(fp)}

	for module in modules:
		for parent_module in module_config.get(module, {}).get('requires', []):
			if parent_module in disabled_modules:
				disabled_modules += [module]
				break

	return list(set(disabled_modules))


def get_enabled_modules(user_data: dict | None = None, *, group: str | None = None) -> list:
	"""
	Retrieve a list of enabled modules, optionally filtering out those disabled for a specific user or group.

	Args:
		user_data (dict | None, optional): A dictionary containing user-specific data, including disabled modules and groups. Defaults to None.
		group (str | None, optional): A specific group to consider for disabled modules. Defaults to None.

	Returns:
		list: A list of enabled modules, excluding those disabled for the specified user or group.
	"""

	module_config: dict | None = db.find_one({'name': 'modules'})
	if module_config is None:
		return []

	modules: list[str] = module_config.get('enabled', [])

	group_config: dict | None = db.find_one({'name': 'groups'})
	groups: dict[str, dict[str, list[str]]] = {} if group_config is None else group_config.get('groups', {})

	disabled_modules: list[str] = []

	if user_data is not None:
		disabled_modules += user_data.get('disabled_modules', [])
		for user_group in user_data.get('groups', []):
			disabled_modules += groups.get(user_group, {}).get('disabled_modules', [])

	if group is not None:
		disabled_modules += groups.get(group, {}).get('disabled_modules', [])

	return [i for i in modules if i not in calculate_disabled_modules(disabled_modules)]


def get_modules(user_data: dict) -> list:
	"""
	Retrieve a list of modules available to a user, excluding any disabled modules based on the user's groups.

	Args:
		user_data (dict): A dictionary containing user information, including their groups.

	Returns:
		list: A list of enabled modules for the user, excluding any disabled modules.
	"""

	module_config: dict | None = db.find_one({'name': 'modules'})
	if module_config is None:
		return []

	modules: list[str] = module_config.get('enabled', [])

	group_config: dict | None = db.find_one({'name': 'groups'})
	groups: dict[str, dict[str, list[str]]] = {} if group_config is None else group_config.get('groups', {})

	disabled_modules: list[str] = []

	for group in user_data.get('groups', []):
		disabled_modules += groups.get(group, {}).get('disabled_modules', [])

	return [i for i in modules if i not in calculate_disabled_modules(disabled_modules)]


def set_module_enabled(module_id: str, enabled: bool, group: str | None) -> None:
	"""
	Enable or disable a module in the database.

	If a group is specified, the module's enabled/disabled state is updated within that group.
	Otherwise, the module's state is updated globally.

	Args:
		module_id (str): The ID of the module to be enabled or disabled.
		enabled (bool): True to enable the module, False to disable it.
		group (str | None): The group within which to update the module's state. If None, the global state is updated.

	Returns:
		None
	"""

	if group is not None:
		groups = db.find_one({'name': 'groups'})
		if groups is None:
			return

		grp = groups.get('groups', {}).get(group, {})
		if grp is None:
			return

		disabled_modules: list[str] = grp.get('disabled_modules', [])
		if enabled and module_id in disabled_modules:
			disabled_modules.remove(module_id)
		elif not enabled and module_id not in disabled_modules:
			disabled_modules += [module_id]

		db.update_one({'name': 'groups'}, {'$set': {
			f'groups.{group}.disabled_modules': disabled_modules,
		}})
		return

	modules = db.find_one({'name': 'modules'})

	if enabled and modules is None:
		db.insert_one({
			'name': 'modules',
			'type': 'list',
			'enabled': [module_id],
		})
		return

	modules = [] if modules is None else modules.get('enabled', [])
	module_is_enabled = module_id in modules

	if enabled == module_is_enabled:
		return  # No change needs to be made

	if enabled:
		modules += [module_id]
	elif module_id in modules:
		modules.remove(module_id)

	db.update_one({'name': 'modules'}, {'$set': {'enabled': modules}})


def update_groups(old_groups: list[str], new_groups: list[str]) -> None:
	"""
	Updates the user counts for groups in the database based on the provided old and new group lists.

	If the 'groups' document does not exist in the database, it creates a new one with the new groups.

	Args:
		old_groups (list[str]): A list of group names that the user was previously a member of.
		new_groups (list[str]): A list of group names that the user is currently a member of.

	Returns:
		None
	"""

	groups = db.find_one({'name': 'groups'})
	if groups is None:
		db.insert_one({
			'name': 'groups',
			'type': 'list',
			'groups': {i: {
				'disabled_modules': [],
				'user_count': 1,
			} for i in new_groups},
		})
		return

	# Decrement old groups
	for i in [i for i in set(old_groups).difference(set(new_groups)) if i in groups['groups']]:
		groups['groups'][i]['user_count'] -= 1
		# Delete group if no users are in it anymore
		if groups['groups'][i]['user_count'] < 1:
			del groups['groups'][i]

	# Increment new groups
	for i in set(new_groups).difference(set(old_groups)):
		if i in groups['groups']:
			groups['groups'][i]['user_count'] += 1
		else:
			groups['groups'][i] = {
				'disabled_modules': [],
				'user_count': 1,
			}

	# Update database
	db.update_one({'name': 'groups'}, {'$set': {'groups': groups['groups']}})


def get_groups() -> list:
	"""
	Retrieve a list of user groups from the database.

	Returns:
		list: A list of groups if the 'groups' document is found, otherwise an empty list.
	"""
	groups = db.find_one({'name': 'groups'})
	return [] if groups is None else [i for i in groups['groups']]


def set_config(name: str, value: str | None) -> None:
	"""
	Sets or deletes a configuration value in the database.

	If the value is None, the configuration entry with the given name is deleted.
	Otherwise, the configuration entry is updated or created with the provided value.

	Args:
		name (str): The name of the configuration setting.
		value (str | None): The value to set for the configuration setting. If None, the setting is deleted.

	Returns:
		None
	"""
	real_name = f'config:{name}'

	if value is None:
		db.delete_one({'name': real_name})
	else:
		db.update_one({'name': real_name}, {'$set': {'value': value, 'type': 'value'}}, upsert=True)


def get_config(name: str) -> str | None:
	"""
	Retrieve the configuration value for a given configuration name.

	Args:
		name (str): The name of the configuration to retrieve.

	Returns:
		str | None: The value of the configuration if found, otherwise None.
	"""
	real_name = f'config:{name}'
	config = db.find_one({'name': real_name})

	if config is None:
		return None

	return config.get('value')


def get_all_configs() -> list:
	"""
	Retrieve all configuration entries from the database.

	Returns:
		list: A list of dictionaries, each containing 'name' and 'value' keys
			  representing the configuration entries.
	"""
	result = []

	for i in db.find({'type': 'value'}):
		if i['name'][0:7] == 'config:':
			result += [{
				'name': i['name'][7::],
				'value': i.get('value'),
			}]

	return result


def get_all_themes() -> list:
	"""
	Retrieve all themes from the database.

	Returns:
		list: A list of all themes found in the database.
	"""
	return [i for i in db.find({'type': 'theme'})]


def create_theme(theme: dict) -> dict:
	"""
	Creates or updates a theme in the database.

	If a theme with the same name already exists, it updates the existing theme.
	Otherwise, it inserts a new theme.

	Args:
		theme (dict): A dictionary containing the theme details.

	Returns:
		dict: The theme that was created or updated.
	"""
	existing_theme = db.find_one({'type': 'theme', 'name': theme.get('name')})
	if existing_theme:
		db.update_one({'type': 'theme', 'name': theme.get('name')}, {'$set': theme})
	else:
		db.insert_one({'type': 'theme', **theme})

	return theme


def delete_theme(name: str) -> dict:
	"""
	Deletes a theme from the database by its name.

	Args:
		name (str): The name of the theme to delete.

	Returns:
		dict: The deleted theme document.

	Raises:
		exceptions.MissingConfig: If the theme with the specified name does not exist.
	"""
	theme = db.find_one({'type': 'theme', 'name': name})
	if theme:
		db.delete_one({'type': 'theme', 'name': name})
		return theme

	raise exceptions.MissingConfig(name)
