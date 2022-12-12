var __template_map = {}

async function update_dom(name, data, instant = false)
{
	var fields = []
	if (typeof name === 'object')
	{
		fields.push(name)
	}
	else
	{
		var elem = document.getElementById(name)
		if (elem)
			fields.push(elem)
		else
			fields = document.querySelectorAll('div[name="' + name + '"]')
	}

	for (var field of fields)
	{
		const template_name = field.attributes.template ? field.attributes.template.value : name

		//Load template only once.
		if (__template_map[template_name] === undefined)
		{
			const template_text = await api.get('templates/' + template_name + '.dot')
			__template_map[template_name] = doT.template(template_text, undefined, {})
		}

		const pagefn = __template_map[template_name]
		if (!instant) $.hide(field)
		field.innerHTML = pagefn((data !== undefined) ? data : field)
		if (!instant) $.show(field)
	}
}

async function template(template_name, data, instant = false)
{
	//show spinner to indicate stuff is loading
	for (var field of document.querySelectorAll('div[name="' + template_name + '"]'))
	{
		if (!instant) $.hide(field)
		field.innerHTML = '<i class="gg-spinner"></i>'
		if (!instant) $.show(field)
	}

	//if data is actually a Promise, update the dom whenever it resolves.
	if (typeof data?.then === 'function')
		data.then(res => { update_dom(template_name, res, instant) })
	else
		await update_dom(template_name, data, instant)
}

//Constantly refresh dom element(s) as long as at least 1 div with the template_name exists.
//Once it no longer exists, stop refreshing.
template.sync = async function(template_name, data_method, frequency = 500, instant = false)
{
	if (!(document.querySelectorAll('div[name="' + template_name + '"]').length)) { return }
	await template(template_name, data_method(), instant)
	setTimeout(() => {
		template.sync(template_name, data_method, frequency, instant)
	}, frequency)
}

export default template
