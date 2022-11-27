var __template_map = {}

async function template(template_name, data)
{
	var pagefn = __template_map[template_name]
	if (pagefn === undefined)
	{
		var script = document.querySelector('script[name="' + template_name + '"]')
		if (script === null)
		{
			//Assume that the template path is "templates/{template_name}.dot"
			script = {
				text: null,
				src: 'templates/' + template_name + '.dot'
			}
		}
		else
		{
			var def = {}
			if (script.attributes.def?.nodeValue)
			{
				for (var i of script.attributes.def.nodeValue.split())
				{
					var def_scr = document.querySelector('script[name="' + i + '"]')
					if (def_scr === null)
					{
						throw 'Error: When loading "' + template_name + '" template, unable to find def "' + i + '"'
					}
					def[i] = def_scr.text
				}
			}
		}

		var text = script.text
		if (script.src)
		{
			text = await api.get(script.src)
		}

		pagefn = doT.template(text, undefined, def)
		__template_map[template_name] = pagefn
	}

	var update_dom = data =>
	{
		document.querySelectorAll('div[name="' + template_name + '"]').forEach(field => {
			if (data)
				field.innerHTML = pagefn(data)
			else
				field.innerHTML = pagefn(field)
		})
	}

	//if data is actually a Promise, update the dom whenever it resolves.
	if (typeof data?.then === 'function')
	{
		data.then(res => {
			update_dom(res)
		})
	}
	else
	{
		update_dom(data)
	}
}

//Constantly refresh dom element(s) as long as at least 1 div with the template_name exists.
//Once it no longer exists, stop refreshing.
template.sync = (template_name, data_method, frequency = 500) =>
{
	if (!(document.querySelectorAll('div[name="' + template_name + '"]').length)) { return }
	template(template_name, data_method())
	setTimeout(() => {
		template.sync(template_name, data_method, frequency)
	}, frequency)
}

export default template
