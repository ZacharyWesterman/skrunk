/*
* Simple helper function for site navigation.
*/
window.navigate = async function(url)
{
	await inject(document.all.body, url)
}

window.dashnav = async function(url)
{
	await inject(document.all.content, url)
}

/*
* Load content from URL into the given field.
*/
window.unload = []
window.inject = async function(field, url)
{
	while (window.unload.length > 0)
	{
		var unload_method = window.unload.pop()
		unload_method()
	}

	//show spinner to indicate stuff is loading
	$.hide(field)
	field.innerHTML = '<i class="gg-spinner"></i>'
	setTimeout(() => $.show(field), 250)

	try {
		var res = await api.get(url)
	} catch (error) {
		await api.handle_query_failure(error)
	}

	//hide DOM element while it's loading
	$.hide(field)

	field.innerHTML = res

	//show element after it's probably finished loading
	setTimeout(() => $.show(field), 250)

	//show spinner to indicate resources are loading
	$.show($('loader'))

	//set custom tag-based field logic
	set_field_logic(field, url)

	for (var script of field.getElementsByTagName('script'))
	{
		if (script.src.length)
		{
			if (script.attributes.async) //async, so allow more scripts to be loaded
			{
				api.get(script.src).then(res => {
					do_script_eval(field, res, script.src, true)
				}).catch(error => {
					throw 'RESPONSE ' + error.status + ' ' + error.statusText
				})
			}
			else //load scripts synchronously
			{
				try {
					res = await api.get(script.src)
				} catch (error) {
					throw 'RESPONSE ' + error.status + ' ' + error.statusText
				}
				await do_script_eval(field, res, script.src, true)
			}
		}
		else //eval inline script text
		{
			await do_script_eval(field, script.text, url, false)
		}
	}

	$.hide($('loader'))
}

//Eval script and (if it errors) give more accurate error info.
async function do_script_eval(DOM, text, url, replaceUrl)
{
	try {
		const objectURL = URL.createObjectURL(new Blob([text], {type: 'text/javascript'}))
		const module = await import(objectURL)
		if (module)
		{
			for (const key in module)
			{
				//Custom onClick logic
				DOM.querySelectorAll(`[click="${key}"]`).forEach(field => {
					field.onclick = module[key]
				})
			}
		}
	} catch (error) {
		report_error(error, url, replaceUrl)
	}
}

window.set_field_logic = async function(DOM, url)
{
	try
	{
		//Enforce field value formatting
		DOM.querySelectorAll(`[format]`).forEach(field => {
			const format = field.getAttribute('format')
			const enforce = $.enforce[format]
			const validate = $.validate[format]

			if (enforce === undefined && validate === undefined)
				throw new Error(`Unknown format type "${format}"`)

			if (enforce !== undefined)
			{
				//Enforce formatting
				const keyup = field.onkeyup
				field.onkeyup = () => {
					if (field.value !== '')
						field.value = enforce(field.value)

					if (typeof keyup === 'function') keyup()
				}
			}

			if (validate !== undefined)
			{
				//Validate on blur
				const blur = field.onblur
				const change = field.onchange
				field.onchange = () => {}
				field.onblur = () => {
					field.value = field.value
					if (field.value === '')
					{
						if (field.required) field.value = field.prevValue
						return
					}

					const valid = validate(field.value)
					if (valid)
					{
						field.classList.remove('invalid')
						if ((typeof change === 'function') && (field.value !== field.prevValue)) change()
						field.prevValue = field.value
						if (typeof blur === 'function') blur()
					}
					else
					{
						field.classList.add('invalid')
						field.value = field.prevValue || field.defaultValue || ''
					}
				}
			}
		})
	} catch (error) {
		report_error(error, url, true)
	}
}

function report_error(error, url, replaceUrl)
{
	var stack = error.stack.trim().split('\n')
	stack = stack[stack.length-1].split(':')
	stack[2] = (replaceUrl ? '@' : stack[2]) + url
	stack[3] = error.lineNumber
	stack[4] = error.columnNumber
	if (replaceUrl)
	{
		stack.shift()
		stack.shift()
	}
	error.stack = stack.join(':')
	console.log(error)
}
