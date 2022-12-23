/*
* Simple helper function for site navigation.
*/
async function navigate(url)
{
	await inject(document.all.body, url)
}

async function dashnav(url)
{
	await inject(document.all.content, url)
}

/*
* Load content from URL into the given field.
*/
window.unload = []
async function inject(field, url)
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

	//Eval script and (if it errors) give more accurate error info.
	async function do_script_eval(text, url, replaceUrl)
	{
		try {
			const objectURL = URL.createObjectURL(new Blob([text], {type: 'text/javascript'}))
			const m = await import(objectURL)
		} catch (error) {
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
	}

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

	for (var script of field.getElementsByTagName('script'))
	{
		if (script.src.length)
		{
			if (script.attributes.async) //async, so allow more scripts to be loaded
			{
				api.get(script.src).then(res => {
					do_script_eval(res, script.src, true)
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
				await do_script_eval(res, script.src, true)
			}
		}
		else //eval inline script text
		{
			await do_script_eval(script.text, url, false)
		}
	}

	$.hide($('loader'))
}
