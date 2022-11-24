var __template_map = {}

async function _(template_name, data)
{
	var pagefn = __template_map[template_name]
	if (pagefn === undefined)
	{
		var script = document.querySelector('script[name="' + template_name + '"]')
		if (script === null)
		{
			throw 'Error: No template found with name "' + template_name + '"'
		}

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
			field.innerHTML = pagefn(data)
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
_.sync = (template_name, data_method, frequency = 500) =>
{
	if (!(document.querySelectorAll('div[name="' + template_name + '"]').length)) { return }
	_(template_name, data_method())
	setTimeout(() => {
		_.sync(template_name, data_method, frequency)
	}, frequency)
}


//Field control and validation
var $ = id => document.getElementById(id)
$.val = id => $(id).value

$.validate = {
	phone: function(field)
	{
		$.enforce.phone(field)

		if (field.value.length === 0)
			field.value = field.defaultValue

		if (field.value.length != 10) {
			field.classList.add('error')
			return false
		} else {
			field.classList.remove('error')
			return true
		}
	},

	number: function(field)
	{
		if (field.validity.valid)
            field.classList.remove('error')
        else
            field.classList.add('error')
	},
}

$.enforce = {
	phone: function(field)
	{
		field.value = field.value.replace(/[^0-9]/g, '')
	},
}
