db = None

def get_enabled_modules() -> list:
	modules = db.find_one({'name': 'modules'})
	return [] if modules is None else modules.get('enabled', [])

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

def add_groups(new_groups: list) -> None:
	groups = db.find_one({'name': 'groups'})
	if groups is None:
		db.insert_one({
			'name': 'groups',
			'type': 'list',
			'groups': list(set(new_groups)),
		})
	else:
		db.update_one({'name': 'groups'}, {'$set': {'groups': list(set(groups['groups'] + new_groups))}})

def get_groups() -> list:
	groups = db.find_one({'name': 'groups'})
	return [] if groups is None else groups['groups']

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
		result += [{
			'name': i['name'],
			'value': i.get('value'),
		}]

	return result
