/*
* Simple helper function for site navigation.
*/
window.navigate = async function(url)
{
	clear_error_message()
	await inject(document.all.body, url)
}

window.dashnav = async function(url)
{
	window.history.replaceState({}, '', '?page='+url)
	clear_error_message()
	await inject(document.all.content, `/html/${url}.html`)

	set_title()
}

window.set_title = function()
{
	//Set page title if page has a title header
	const header = document.querySelector('div[class="page"]>h1')
	if (header)
	{
		for (const child of header.childNodes)
		{
			if (child.nodeType === 3) //Text node
			{
				const text = child.textContent.trim()
				if (text !== '')
				{
					document.title = text
					break
				}
			}
		}
	}
}

/*
* Load content from URL into the given field.
*/
window.unload = []
window.inject = async function(field, url)
{
	while (window.unload.length > 0)
	{
		const unload_method = window.unload.pop()
		if (unload_method?.constructor?.name === 'AsyncFunction')
			await unload_method()
		else
			unload_method()
	}

	//show spinner to indicate stuff is loading
	$.hide(field)
	field.innerHTML = '<i class="gg-spinner"></i>'
	setTimeout(() => $.show(field), 250)

	let res
	try {
		res = await api.get(url)
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

	let async_evals = []

	for (const script of field.getElementsByTagName('script'))
	{
		let evaluate = undefined
		if (script.src.length)
		{
			evaluate = async () => {
				return await do_script_eval(field, null, script.src, true)
			}
		}
		else //eval inline script text
		{
			evaluate = async () => {
				return await do_script_eval(field, script.text, url, false)
			}
		}

		async_evals.push(script.attributes.async ? evaluate() : evaluate)
	}

	//wait for async evals to finish
	let module = {}
	for (const item of async_evals)
	{
		const new_mod = await (typeof item === 'function' ? item() : item)
		if (!new_mod) continue

		//Always run init method on src load.
		if (typeof new_mod.init === 'function')
		{
			new_mod.init()
		}

		module = {
			...module,
			...new_mod,
		}
	}

	//set custom tag-based field logic
	set_field_logic(field, url, module)

	$.hide($('loader'))
}

//Eval script and (if it errors) give more accurate error info.
async function do_script_eval(DOM, text, url, imported)
{
	try {
		if (imported)
		{
			return await import(url) || {}
		}
		else
		{
			const objectURL = URL.createObjectURL(new Blob([text], {type: 'text/javascript'}))
			return await import(objectURL) || {}
		}
	} catch (error) {
		report_error(error, url, imported)
	}
}

function set_trigger(field, attr, trigger)
{
	if (!$.on[attr])
		throw new Error(`Error: *${attr} trigger not implemented for *${trigger} action.`)

	if (!$[trigger])
		throw new Error(`Error: *${attr} trigger exists, but *${trigger} action not implemented.`)

	$.on[attr](field, $[trigger])
}

function parent_module(DOM)
{
	let element = DOM.parentElement
	while (element)
	{
		if (element.module) return element.module
		element = element.parentElement
	}
	return {}
}

function scoped_eval(context, expr)
{
	const evaluator = Function.apply(null, [...Object.keys(context), 'expr', 'return eval("expr = undefined;" + expr)'])
	return function () {
		evaluator.apply(null, [...Object.values(context), expr])
	}
}

window.set_field_logic = async function(DOM, url, module)
{

	DOM.module = {
		...parent_module(DOM),
		...module,
	}

	try
	{
		//Custom logic for *click (onclick), *blur (onblur), and *change (onchange) methods
		const attrs = ['click', 'blur', 'change', 'enter', 'escape', 'tab', 'bind']
		for (const attr of attrs)
		{
			DOM.querySelectorAll(`[\\*${attr}]`).forEach(field => {
				const key = field.getAttribute(`*${attr}`)

				if (key[0] === '*')
				{
					set_trigger(field, attr, key.substring(1))
					return
				}

				const split_point = key.indexOf('(')
				if (split_point > -1)
				{
					//If we're running the function with params
					const funcname = key.substring(0, split_point)
					if (!['$','_'].includes(funcname[0]) && typeof DOM.module[funcname] !== 'function' && typeof window[funcname] !== 'function')
						throw new Error(`Unknown action for *${attr} attribute: "${funcname}" export not found.`)

					const scope = scoped_eval(DOM.module, key)
					if (attr === 'bind')
						$.bind(field, () => { scope() })
					else if ($.on[attr])
						$.on[attr](field, scope)
					else
						field[`on${attr}`] = () => { scope() }
				}
				else
				{
					//If we're not running the function with params,
					if (!['$','_'].includes(key[0]) && typeof DOM.module[key] !== 'function')
						throw new Error(`Unknown action for *${attr} attribute: "${key}" export not found.`)

					//can just put in the name and this will pass in the field as 1st param
					if (attr === 'bind')
						$.bind(field, () => { DOM.module[key](field) })
					else if ($.on[attr])
						$.on[attr](field, DOM.module[key])
					else
						field[`on${attr}`] = () => { DOM.module[key](field) }
				}
			})
		}

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
						if (field.required)
							field.value = field.prevValue || field.defaultValue || ''
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

		//At the very end, run all *load (onload) selectors
		DOM.querySelectorAll(`[\\*load]`).forEach(field => {
			const key = field.getAttribute('*load')
			const split_point = Math.min(key.indexOf('(') || Math.infinity, key.indexOf('.') || Math.infinity)
			if (split_point > -1 && split_point !== Math.infinity)
			{
				//If we're running the function with params
				const funcname = key.substring(0, split_point)
				if (window[funcname] !== undefined || DOM.module[funcname] !== undefined)
				{
					//evaluate immediately
					scoped_eval(DOM.module, key)()

				}
				else
				{
					throw new Error(`Unknown action for *load attribute: "${funcname}" export not found.`)
				}
			}
			else
			{
				//If we're not running the function with params,
				if (typeof DOM.module[key] !== 'function')
					throw new Error(`Unknown action for *load attribute: "${key}" export not found.`)

				//can just put in the name and this will pass in the field as 1st param
				DOM.module[key](field)
			}
		})
	} catch (error) {
		report_error(error, url, true)
	}
}

function report_error(error, url, replaceUrl)
{
	let stack = error.stack.trim().split('\n')
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
	console.error(error)
	window.show_error_message(error)
}
