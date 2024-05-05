from pymongo.collection import Collection
db: Collection = None

def get_enabled_modules(user_data: dict|None = None) -> list:
	modules = db.find_one({'name': 'modules'})
	if modules is None:
		return []

	if user_data is None:
		return modules.get('enabled', [])

	groups = db.find_one({'name': 'groups'})
	groups: dict[str, dict[str, list[str]]] = {} if groups is None else groups.get('groups', {})

	user_disabled_modules: list[str] = user_data.get('disabled_modules', [])
	group_disabled_modules: list[str] = []

	for group in user_data.get('groups', []):
		group_disabled_modules += groups.get(group, {}).get('disabled_modules', [])

	return [i for i in modules.get('enabled', []) if i not in user_disabled_modules and i not in group_disabled_modules]

def get_modules(user_data: dict) -> list:
	modules = db.find_one({'name': 'modules'})
	if modules is None:
		return []

	groups = db.find_one({'name': 'groups'})
	groups: dict[str, dict[str, list[str]]] = {} if groups is None else groups.get('groups', {})

	group_disabled_modules: list[str] = []

	for group in user_data.get('groups', []):
		group_disabled_modules += groups.get(group, {}).get('disabled_modules', [])

	return [i for i in modules.get('enabled', []) if i not in group_disabled_modules]

def set_module_enabled(module_id: str, enabled: bool) -> None:
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
	else:
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
