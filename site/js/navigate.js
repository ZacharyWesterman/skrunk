/**
 * A simple helper function for site navigation.
 * @param {string} url The url to fetch and insert into the document.
 */
window.navigate = async function (url) {
	clear_error_message()
	await inject(document.all.body, url)
}

window.dashnav = async function (url) {
	environment.set_param('page', url)
	clear_error_message()
	await inject(document.all.content, `/html/${url}.html`)

	set_title()
}

window.set_title = function () {
	//Set page title if page has a title header
	const header = document.querySelector('div[class="page"]>h1')
	if (header) {
		for (const child of header.childNodes) {
			if (child.nodeType === 3) //Text node
			{
				const text = child.textContent.trim()
				if (text !== '') {
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
window.inject = async function (field, url) {
	field = $(field)
	$.on.detach.resize() //Stop watching for any resize events the previous page might be watching for.

	while (window.unload.length > 0) {
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

	for (const script of field.getElementsByTagName('script')) {
		let evaluate = undefined
		if (script.src.length) {
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
	let initializers = []
	for (const item of async_evals) {
		const new_mod = await (typeof item === 'function' ? item() : item)
		if (!new_mod) continue

		//Always run init method on src load.
		if (typeof new_mod.init === 'function') {
			initializers.push(new_mod.init)
		}

		module = {
			...module,
			...new_mod,
		}
	}

	//set custom tag-based field logic
	set_field_logic(field, url, module)

	//Always run init method on src load.
	for (const init of initializers) { init() }

	$.hide($('loader'))
}

//Eval script and (if it errors) give more accurate error info.
async function do_script_eval(DOM, text, url, imported) {
	try {
		if (imported) {
			return await import(url) || {}
		}
		else {
			const objectURL = URL.createObjectURL(new Blob([text], { type: 'text/javascript' }))
			return await import(objectURL) || {}
		}
	} catch (error) {
		report_error(error, url, imported)
	}
}

function set_trigger(field, attr, trigger) {
	if (!$.on[attr])
		throw new Error(`Error: *${attr} trigger not implemented for *${trigger} action.`)

	if (!$[trigger])
		throw new Error(`Error: *${attr} trigger exists, but *${trigger} action not implemented.`)

	$.on[attr](field, $[trigger])
}

function parent_module(DOM) {
	let element = DOM.parentElement
	while (element) {
		if (element.module) return element.module
		element = element.parentElement
	}
	return {}
}

function scoped_eval(context, expr) {
	const evaluator = Function.apply(null, [...Object.keys(context), 'expr', 'return eval("expr = undefined;" + expr)'])
	return function () {
		evaluator.apply(null, [...Object.values(context), expr])
	}
}

window.set_field_logic = async function (DOM, url, module) {

	DOM.module = {
		...parent_module(DOM),
		...module,
	}

	try {
		//Custom logic for *click (onclick), *blur (onblur), and *change (onchange) methods
		const attrs = ['click', 'blur', 'change', 'enter', 'escape', 'tab', 'bind', 'toggles', 'expand']
		for (const attr of attrs) {
			DOM.querySelectorAll(`[\\*${attr}]`).forEach(field => {
				const key = field.getAttribute(`*${attr}`)

				if (key[0] === '*') {
					set_trigger(field, attr, key.substring(1))
					return
				}

				if (attr === 'toggles') {
					field.addEventListener('click', () => {
						$.toggle_expand(key)
						//Automatically flip any "expand" arrows to reflect whether content is expanded
						$.sync_invert_to_expand(field, key)
					})

					//Automatically flip any "expand" arrows to reflect whether content is expanded
					$.sync_invert_to_expand(field, key)
					return
				}

				if (attr === 'expand_invert') return

				const split_point = key.indexOf('(')
				if (split_point > -1) {
					//If we're running the function with params
					const funcname = key.substring(0, split_point)
					if (!['$', '_'].includes(funcname[0]) && typeof DOM.module[funcname] !== 'function' && typeof window[funcname] !== 'function')
						throw new Error(`Unknown action for *${attr} attribute: "${funcname}" export not found.`)

					const scope = scoped_eval(DOM.module, key)
					if (attr === 'bind')
						$.bind(field, () => { scope() })
					else if ($.on[attr])
						$.on[attr](field, scope)
					else
						field[`on${attr}`] = () => { scope() }
				}
				else {
					//If we're not running the function with params,
					if (!['$', '_'].includes(key[0]) && typeof DOM.module[key] !== 'function')
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

		//Bind any ternary checkboxes
		DOM.querySelectorAll('input[type="checkbox"][ternary]').forEach(field => {
			(method => {
				field.onclick = () => {
					field.state = [1, 2, 0][field.state]
					field.checked = field.state === 2
					field.indeterminate = field.state === 1

					if (method) method(field)
				}
			})(field.onclick)

			//Initialize field state
			field.indeterminate = field.getAttribute('indeterminate') !== null
			field.state = field.checked ? 2 : (field.indeterminate ? 1 : 0)
		})

		//Enforce field value formatting
		DOM.querySelectorAll(`[format]`).forEach(field => {
			const format = field.getAttribute('format')
			const enforce = $.enforce[format]
			const validate = $.validate[format]

			if (enforce === undefined && validate === undefined)
				throw new Error(`Unknown format type "${format}"`)

			if (enforce !== undefined) {
				//Enforce formatting
				const keyup = field.onkeyup
				field.onkeyup = () => {
					if (field.value !== '')
						field.value = enforce(field.value)

					if (typeof keyup === 'function') keyup()
				}
			}

			if (validate !== undefined) {
				//Validate on blur
				const blur = field.onblur
				const change = field.onchange
				field.onchange = () => { }
				field.onblur = () => {
					field.value = field.value
					if (field.value === '') {
						if (field.required)
							field.value = field.prevValue || field.defaultValue || ''
						return
					}

					const valid = validate(field.value)
					if (valid) {
						field.classList.remove('invalid')
						if ((typeof change === 'function') && (field.value !== field.prevValue)) change()
						field.prevValue = field.value
						if (typeof blur === 'function') blur()
					}
					else {
						field.classList.add('invalid')
						field.value = field.prevValue || field.defaultValue || ''
					}
				}
			}
		})

		//Update any rich text editors
		DOM.querySelectorAll('input[type="richtext"]').forEach(field => {
			$.editor.new(field)
		})

		//Update any photo upload buttons
		DOM.querySelectorAll('input[type="photo"]').forEach(field => {
			if (!EnabledModules.includes('files')) {
				const new_field = document.createElement('span')
				new_field.classList.add('suppress')
				new_field.innerText = 'File uploads are disabled.'
				field.replaceWith(new_field)
				return
			}

			const new_field = document.createElement('span')
			const upload_btn = document.createElement('button')
			const delete_btn = document.createElement('button')
			const cam_icon = document.createElement('i')
			const del_icon = document.createElement('i')
			const br = document.createElement('br')
			const img = document.createElement('img')
			const progressbar = document.createElement('progress')

			del_icon.classList.add('fa-solid', 'fa-trash', 'fa-lg')
			cam_icon.classList.add('fa-solid', 'fa-camera', 'fa-lg')
			upload_btn.style.marginRight = '4rem'
			upload_btn.classList.add('icon', 'clickable')
			delete_btn.classList.add('icon', 'clickable')
			img.classList.add('thumbnail')
			img.style.display = 'none'
			img.id = field.id
			img.tags = field.getAttribute('tags')?.toLowerCase()?.split(' ')
			$.hide(img)
			$.hide(progressbar)

			upload_btn.appendChild(cam_icon)
			delete_btn.appendChild(del_icon)
			new_field.append(upload_btn, delete_btn, br, img, progressbar)

			img.wipe = () => {
				if (img.blob_id) {
					//Try to delete the blob. Doesn't really matter if it's successful, the blob is ephemeral so will get deleted at some point anyway.
					mutate.blobs.delete(img.blob_id).catch(() => { })
					delete img.blob_id
				}

				$.hide(img, true).then(() => img.src = '')
				$.hide(progressbar, true)
				progressbar.removeAttribute('value')
				img.onclick = () => { }
				img.classList.remove('clickable')
			}

			img.clear = () => {
				if (img.blob_id) {
					delete img.blob_id
				}

				$.hide(img, true).then(() => img.src = '')
				$.hide(progressbar, true)
				progressbar.removeAttribute('value')
				img.onclick = () => { }
				img.classList.remove('clickable')
			}

			upload_btn.onclick = async () => {
				const file = await api.file_prompt('image/*', false, 'camera').catch(() => null)

				if (file === null) return

				$.show(progressbar)

				const image = (await api.upload(file, ({ loaded, total }) => {
					progressbar.value = loaded / total
				}, false, img.tags, false, true))[0]
				progressbar.removeAttribute('value')

				const res = await query.blobs.single(image.id)

				img.src = `preview/${res.thumbnail}`
				img.alt = 'FAILED TO LOAD THUMBNAIL'
				img.blob_id = image.id
				img.classList.add('clickable')
				img.onclick = () => {
					_.modal.image(`blob/${res.id}${res.ext}`)
				}

				await $.hide(progressbar, true)
				$.show(img)
			}

			delete_btn.onclick = async () => {
				img.wipe()
			}

			field.replaceWith(new_field)
		})

		//At the very end, run all *load (onload) selectors
		DOM.querySelectorAll(`[\\*load]`).forEach(field => {
			const key = field.getAttribute('*load')
			const split_point = Math.min(key.indexOf('(') || Math.infinity, key.indexOf('.') || Math.infinity)
			if (split_point > -1 && split_point !== Math.infinity) {
				//If we're running the function with params
				const funcname = key.substring(0, split_point)
				if (window[funcname] !== undefined || DOM.module[funcname] !== undefined) {
					//evaluate immediately
					scoped_eval(DOM.module, key)()

				}
				else {
					throw new Error(`Unknown action for *load attribute: "${funcname}" export not found.`)
				}
			}
			else {
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

function report_error(error, url, replaceUrl) {
	let stack = error.stack.trim().split('\n')
	stack = stack[stack.length - 1].split(':')
	stack[2] = (replaceUrl ? '@' : stack[2]) + url
	stack[3] = error.lineNumber
	stack[4] = error.columnNumber
	if (replaceUrl) {
		stack.shift()
		stack.shift()
	}
	error.stack = stack.join(':')
	console.error(error)
	window.show_error_message(error)
}
