var __template_map = {}

async function update_dom(name, data)
{
	var fields = document.querySelectorAll('div[name="' + name + '"]')
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
		field.innerHTML = pagefn((data !== undefined) ? data : field)
	}
}

async function template(template_name, data)
{
	//if data is actually a Promise, update the dom whenever it resolves.
	if (typeof data?.then === 'function')
		data.then(res => { update_dom(template_name, res) })
	else
		await update_dom(template_name, data)
}

//Constantly refresh dom element(s) as long as at least 1 div with the template_name exists.
//Once it no longer exists, stop refreshing.
template.sync = async function(template_name, data_method, frequency = 500)
{
	if (!(document.querySelectorAll('div[name="' + template_name + '"]').length)) { return }
	await template(template_name, data_method())
	setTimeout(() => {
		template.sync(template_name, data_method, frequency)
	}, frequency)
}

export default template
