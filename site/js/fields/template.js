let __template_map = {}

async function update_dom(name, data, instant = false) {
	for (let field of find_fields(name)) {
		const template_name = field.attributes.template ? field.attributes.template.value : name
		const url = '/templates/' + template_name + '.dot'
		//Load template only once.
		if (__template_map[template_name] === undefined) {
			const template_text = await api.get(url)
			__template_map[template_name] = doT.template(template_text, undefined, {})
		}

		const pagefn = __template_map[template_name]
		if (!instant) $.hide(field)
		const txt = pagefn((data !== undefined) ? data : field)
		field.innerHTML = txt
		if (!instant) $.show(field)
		set_field_logic(field, url, {})
	}
}

function find_fields(name) {
	let fields = []
	if (typeof name === 'object') {
		fields.push(name)
	}
	else {
		const elem = document.getElementById(name)
		if (elem)
			fields.push(elem)
		else
			fields = document.querySelectorAll('[name="' + name + '"]')
	}
	return fields
}

async function await_promises(data) {
	if (!data) return null

	if (typeof data?.then === 'function') {
		return await data
	}
	else if (typeof data === 'object') {
		let changed = false
		for (let i of Object.keys(data)) {
			const res = await await_promises(data[i])
			if (res !== null) {
				changed = true
				data[i] = res
			}
		}

		if (changed) return data
	}

	return null
}

async function template(template_name, data, instant = false) {
	//show spinner to indicate stuff is loading
	for (let field of find_fields(template_name)) {
		if (!instant) $.hide(field)
		field.innerHTML = '<i class="gg-spinner"></i>'
		if (!instant) $.show(field)
	}

	const res = await await_promises(data)
	await update_dom(template_name, (res !== null) ? res : data, instant)
}

//Constantly refresh dom element(s) as long as at least 1 div with the template_name exists.
//Once it no longer exists, stop refreshing.
let SyncList = {}
template.sync = async function (template_name, data_method, frequency = 500, instant = false) {
	const val = SyncList[template_name]
	SyncList[template_name] = frequency

	const load_func = async () => {
		if (!(find_fields(template_name).length)) {
			delete SyncList[template_name]
			return
		}

		let loaded_data = data_method()
		if (typeof loaded_data?.then === 'function') {
			loaded_data = await loaded_data
		}
		await template(template_name, loaded_data, instant)
	}

	if (val !== undefined) {
		await load_func() //Sync once immediately
		return //Don't queue more syncing if already syncing
	}

	const sync_func = async () => {
		await load_func()
		setTimeout(() => sync_func(), SyncList[template_name])
	}

	await sync_func()
}

export default template
