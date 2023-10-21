import Validate from './fields/validate.js'
import Enforce from './fields/enforce.js'
import Template from './fields/template.js'
import Modal from './fields/modal.js'
import Events from './fields/events.js'
import Control from './fields/control.js'
// import Stackedit from 'https://unpkg.com/stackedit-js@1.0.7/docs/lib/stackedit.min.js'

let _ = Template
_.modal = Modal

function get_css_styles()
{
	for (let sheet of document.styleSheets)
	{
		for (let rule of sheet.cssRules)
		{
			if (rule.href === '/css/theme.css')
			{
				return rule.styleSheet.rules[0].style
			}
		}
	}

	return []
}

_.css = {
	vars: () => get_css_styles(),
	set_var: (name, value) => document.querySelector(':root').style.setProperty(name, value.trim()),
	get_var: name => getComputedStyle(document.querySelector(':root')).getPropertyValue(name).trim(),
	wipe: () => {for (const i of _.css.vars()) _.css.set_var(i, '')},
}

//Field control and validation
let $ = field => ((typeof field === 'object') ? field : document.getElementById(field)) || document.getElementsByName(field)[0]
$.val = id => $(id)?.value
$.set = (id, value) => {
	$(id).value = value
	$(id).prevValue = value
}
$.toggle_expand = (id, expand) =>
{
	const field = $(id)
	field.classList.toggle('expanded', expand)
	const attr = field.getAttribute('*expand_invert')
	if (attr)
	{
		$.sync_invert_to_expand(attr, field)
	}
}

$.sync_invert_to_expand = (field1, field2) =>
{
	for (const i of $(field1).getElementsByClassName('fa-angles-down'))
	{
		i.classList.toggle('inverted', $(field2).classList.contains('expanded'))
	}
}

$.show = (id, fade = true) => {
	let field = $(id)
	if (!field) return
	field.style.display = ''
	setTimeout(() => {
		field.classList.add('fade')
		field.classList.remove('hidden')
		field.classList.add('visible')
	}, 50)
}
$.hide = (id, fade = false, remove = true) => {
	let field = $(id)
	if (!field) return
	let classes = field.classList
	classes.toggle('fade', fade)
	classes.remove('visible')
	classes.add('hidden')
	if (remove)
	{
		if (fade)
			setTimeout(() => field.style.display = 'none', 300)
		else
			$(id).style.display = 'none'
	}
}
$.toggle = (id, state, fade = true) => {
	if (state === undefined) state = $(id).classList.contains('hidden')

	const func = state ? $.show : $.hide
	func(id, fade)
}

$.invalid = (id, state = true) => {
	$(id).classList.toggle('invalid', state)
}

$.valid = (id, state = true) => {
	$(id).classList.toggle('invalid', !state)
}

$.flash = id => {
	$.invalid(id)
	setTimeout(() => $.valid(id), 350)
}

$.blink = id => {
	$.show(id)
	setTimeout(() => {
		$.hide(id, true)
	}, 500)
}

$.validate = Validate
$.enforce = Enforce
$.on = Events
$.next = Control.next
$.prev = Control.prev

$.bind = function(field, method, frequency = 500, run_on_start = false)
{
	$(field).__prev = $(field).value
	if (run_on_start) method()

	let last_run = Date.now()
	let run_scheduled = false

	function change_func(force)
	{
		let f = $(field)

		last_run = Date.now()
		if (f.__prev === f.value) return
		if (run_scheduled && !force) return

		run_scheduled = true
		function sync_method()
		{

			//only sync when field hasn't changed for at least {frequency} ms.
			const synced_recently = Date.now() - last_run < frequency
			if ((f.__prev === f.value) || (synced_recently && !force))
			{
				setTimeout(sync_method, frequency)
				return
			}

			f.__prev = f.value

			if (typeof method.then === 'function')
			{
				last_run = Date.now()
				run_scheduled = false
				method()
			}
			else
			{
				last_run = Date.now()
				run_scheduled = false
				method()
			}
		}

		setTimeout(sync_method, force ? 10 : frequency)
	}

	$(field).addEventListener('keyup', () => change_func(false))
	$(field).addEventListener('change', () => change_func(true))
}

$.wipe = (field, value = '') =>
{
	$(field).__prev = $(field).value = value
}

$.editor = {
	open: async function (text = '')
	{
		return new Promise(resolve => {
			const stackedit = new Stackedit()

			stackedit.openFile({
				name: 'Filename',
				content: {
					text: text
				}
			})

			let editor_file

			stackedit.on('fileChange', file => {
				editor_file = file
			})

			stackedit.on('close', () => {
				resolve({
					text: editor_file.content.text,
					html: editor_file.content.html,
				})
			})
		})
	},

	md_to_html: async function (text)
	{
		return new Promise(resolve => {
			const stackedit = new Stackedit()

			stackedit.openFile({
				name: 'Filename',
				content: {
					text: text
				}
			}, true /*Don't open the editor, just convert text to html*/)

			stackedit.on('fileChange', file => {
				resolve(file.content.html)
			})
		})
	},
}

$.all = name => document.getElementsByName(name)

//Update globals $ (fields) and _ (screen)
window.$ = $
window._ = _
