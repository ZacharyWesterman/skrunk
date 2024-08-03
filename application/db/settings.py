import json
from pymongo.collection import Collection
import application.exceptions as exceptions

db: Collection = None

def calculate_disabled_modules(disabled_modules: list[str]) -> list[str]:
	modules = db.find_one({'name': 'modules'})
	if modules is None:
		return []

	modules: list[str] = modules.get('enabled', [])

	with open('site/config/modules.json', 'r') as fp:
		module_config = { i['id']: i for i in json.load(fp) }

	for module in modules:
		for parent_module in module_config.get(module, {}).get('requires', []):
			if parent_module in disabled_modules:
				disabled_modules += [module]
				break

	return list(set(disabled_modules))

def get_enabled_modules(user_data: dict|None = None, *, group: str|None = None) -> list:
	modules = db.find_one({'name': 'modules'})
	if modules is None:
		return []

	modules: list[str] = modules.get('enabled', [])

	groups = db.find_one({'name': 'groups'})
	groups: dict[str, dict[str, list[str]]] = {} if groups is None else groups.get('groups', {})

	disabled_modules: list[str] = []

	if user_data is not None:
		disabled_modules += user_data.get('disabled_modules', [])
		for user_group in user_data.get('groups', []):
			disabled_modules += groups.get(user_group, {}).get('disabled_modules', [])

	if group is not None:
		disabled_modules += groups.get(group, {}).get('disabled_modules', [])

	return [i for i in modules if i not in calculate_disabled_modules(disabled_modules)]

def get_modules(user_data: dict) -> list:
	modules = db.find_one({'name': 'modules'})
	if modules is None:
		return []

	modules: list[str] = modules.get('enabled', [])

	groups = db.find_one({'name': 'groups'})
	groups: dict[str, dict[str, list[str]]] = {} if groups is None else groups.get('groups', {})

	disabled_modules: list[str] = []

	for group in user_data.get('groups', []):
		disabled_modules += groups.get(group, {}).get('disabled_modules', [])

	return [i for i in modules if i not in calculate_disabled_modules(disabled_modules)]

def set_module_enabled(module_id: str, enabled: bool, group: str|None) -> None:
	if group is not None:
		groups = db.find_one({'name': 'groups'})
		if groups is None: return

		grp = groups.get('groups', {}).get(group, {})
		if grp is None: return

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
		return #No change needs to be made

	if enabled:
		modules += [module_id]
	elif module_id in modules:
		modules.remove(module_id)

	db.update_one({'name': 'modules'}, {'$set': {'enabled': modules}})

def add_groups(new_groups: list[str]) -> None:
	groups = db.find_one({'name': 'groups'})
	if groups is None:
		db.insert_one({
			'name': 'groups',
			'type': 'list',
			'groups': { i: {
				'disabled_modules': [],
			} for i in new_groups },
		})
	else:
		for i in new_groups:
			if i not in groups['groups'][i]:
				groups['groups'][i] = {
					'disabled_modules': [],
				}

		db.update_one({'name': 'groups'}, {'$set': {'groups': groups['groups']}})

def get_groups() -> list:
	groups = db.find_one({'name': 'groups'})
	return [] if groups is None else [ i for i in groups['groups'] ]

def set_config(name: str, value: str|None) -> None:
	real_name = f'config:{name}'

	if value is None:
		db.delete_one({'name': real_name})
	else:
		db.update_one({'name': real_name}, {'$set': {'value': value, 'type': 'value'}}, upsert=True)

def get_config(name: str) -> str|None:
	real_name = f'config:{name}'
	config = db.find_one({'name': real_name})

	if config is None:
		return None

	return config.get('value')

def get_all_configs() -> list:
	result = []

	for i in db.find({'type': 'value'}):
		if i['name'][0:7] == 'config:':
			result += [{
				'name': i['name'][7::],
				'value': i.get('value'),
			}]

	return result

def get_all_themes() -> list:
	return [i for i in db.find({'type': 'theme'})]

def create_theme(theme: dict) -> dict:
	existing_theme = db.find_one({'type': 'theme', 'name': theme.get('name')})
	if existing_theme:
		db.update_one({'type': 'theme', 'name': theme.get('name')}, {'$set': theme})
	else:
		db.insert_one({'type': 'theme', **theme})

	return theme

def delete_theme(name: str) -> dict:
	theme = db.find_one({'type': 'theme', 'name': name })
	if theme:
		db.delete_one({'type': 'theme', 'name': name })
		return theme

	raise exceptions.MissingConfig(name)
