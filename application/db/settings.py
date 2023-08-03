db = None

def get_enabled_modules() -> list:
	modules = db.find_one({'name': 'modules'})
	return [] if modules is None else modules.get('enabled', [])

def set_module_enabled(module_id: str, enabled: bool) -> None:
	modules = db.find_one({'name': 'modules'})

	if enabled and modules is None:
		db.insert_one({
			'name': 'modules',
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