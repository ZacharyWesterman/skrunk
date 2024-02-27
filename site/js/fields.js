import Validate from './fields/validate.js'
import Enforce from './fields/enforce.js'
import Template from './fields/template.js'
import Modal from './fields/modal.js'
import Events from './fields/events.js'
import Control from './fields/control.js'

let _ = Template
_.modal = Modal

function get_css_styles()
{
	for (const sheet of document.styleSheets)
	{
		if ('cssRules' in sheet) continue;

		for (const rule of sheet.cssRules)
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
let $ = field => {
	//Handle rich text editors
	if ($._EDITORS[field])
	{
		return {
			self: $._EDITORS[field],
			id: field,
			set value(text)
			{
				$._EDITORS[field].value(text)
			},
			get value()
			{
				return $._EDITORS[field].value()
			},
		}
	}

	return ((typeof field === 'object') ? field : document.getElementById(field)) || document.getElementsByName(field)[0]
}
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
	const f = $(field1)
	if (!f) return
	for (const i of f.getElementsByClassName('fa-angles-down'))
	{
		i.classList.toggle('inverted', $(field2).classList.contains('expanded'))
	}
}

$.show = (id, fade = true) => {
	return new Promise(resolve => {
		let field = $(id)
		if (!field) return
		field.style.display = ''
		setTimeout(() => {
			field.classList.add('fade')
			field.classList.remove('hidden')
			field.classList.add('visible')
			resolve()
		}, 50)
	})
}
$.hide = (id, fade = false, remove = true) => {
	return new Promise(resolve => {
		let field = $(id)
		if (!field)
		{
			resolve()
			return
		}
		let classes = field.classList
		classes.toggle('fade', fade)
		classes.remove('visible')
		classes.add('hidden')
		if (remove)
		{
			if (fade)
			{
				setTimeout(() => {
					field.style.display = 'none'
					resolve()
				}, 300)
			}
			else
			{
				$(id).style.display = 'none'
				resolve()
			}
		}
		else resolve()
	})
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
	if ($(id).wipe)
	{
		const icon = $(id).parentElement.children[0].children[0]
		icon.classList.toggle('invalid-fg', true)
		setTimeout(() => icon.classList.toggle('invalid-fg', false), 350)
	}
	else
	{
		$.invalid(id)
		setTimeout(() => $.valid(id), 350)
	}
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

$.all = name => document.getElementsByName(name)

$._EDITORS = {}
$.editor = id =>
{
	return $._EDITORS[id]
}
$.editor.new = field =>
{
	const id = (typeof field === 'string') ? field : (field.id || '---')
	$._EDITORS[id] = new SimpleMDE({element: $(field)})
}
$.editor.del = id => delete $._EDITORS[id]

//Update globals $ (fields) and _ (screen)
window.$ = $
window._ = _
