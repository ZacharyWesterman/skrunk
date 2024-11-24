import Validate from './fields/validate.js'
import Enforce from './fields/enforce.js'
import Template from './fields/template.js'
import Modal from './fields/modal.js'
import Events from './fields/events.js'
import Control from './fields/control.js'

let _ = Template
_.modal = Modal

function get_css_styles() {
	for (const sheet of document.styleSheets) {
		try {
			for (const rule of sheet.cssRules) {
				if (rule.href === '/css/theme.css') {
					return rule.styleSheet.rules[0].style
				}
			}
		}
		catch (e) {
			//console.warn(e)
		}
	}

	return []
}

_.css = {
	vars: () => get_css_styles(),
	set_var: (name, value) => document.querySelector(':root').style.setProperty(name, value.trim()),
	get_var: name => getComputedStyle(document.querySelector(':root')).getPropertyValue(name).trim(),
	wipe: () => { for (const i of _.css.vars()) _.css.set_var(i, '') },
}

//Field control and validation
let $ = (field, include_all = false) => {
	let fields = []

	//Handle rich text editors
	if ($._EDITORS[field]) {
		fields.push({
			self: $._EDITORS[field],
			id: field,
			set value(text) {
				$._EDITORS[field].value(text)
			},
			get value() {
				return $._EDITORS[field].value()
			},
		})

		if (!include_all) return fields[0]
	}

	if (typeof field === 'object') {
		fields.push(field)
	}

	let elem = document.getElementById(field)
	if (elem) {
		fields.push(elem)
	}

	document.getElementsByName(field).forEach(elem => {
		fields.push(elem)
	})

	return include_all ? fields : fields[0]
}

$.val = id => $(id)?.value
$.set = (id, value) => {
	$(id).value = value
	$(id).prevValue = value
}

$.checked = id => $(id).indeterminate ? null : $(id).checked

$.toggle_expand = (id, expand) => {
	const fields = $(id, true)
	for (let field of fields) {
		field.classList.toggle('expanded', expand)
		const attr = field.getAttribute('*expand_invert')
		if (attr) {
			$.sync_invert_to_expand(attr, field)
		}
	}
}

$.sync_invert_to_expand = (field1, field2) => {
	const f = $(field1)
	if (!f) return
	for (const i of f.getElementsByClassName('fa-angles-down')) {
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
		if (!field) {
			resolve()
			return
		}
		let classes = field.classList
		classes.toggle('fade', fade)
		classes.remove('visible')
		classes.add('hidden')
		if (remove) {
			if (fade) {
				setTimeout(() => {
					field.style.display = 'none'
					resolve()
				}, 300)
			}
			else {
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
	if ($(id).wipe) {
		const icon = $(id).parentElement.children[0].children[0]
		icon.classList.toggle('invalid-fg', true)
		setTimeout(() => icon.classList.toggle('invalid-fg', false), 350)
	}
	else {
		$.invalid(id)
		setTimeout(() => $.valid(id), 350)
	}
}

$.blink = (id, invert = false) => {
	$.toggle(id, !invert, true)
	setTimeout(() => {
		$.toggle(id, invert, true)
	}, 500)
}

$.validate = Validate
$.enforce = Enforce
$.on = Events
$.next = Control.next
$.prev = Control.prev

$.bind = function (field, method, frequency = 500, run_on_start = false) {
	$(field).__prev = $(field).value
	if (run_on_start) method()

	let last_run = Date.now()
	let run_scheduled = false

	function change_func(force) {
		let f = $(field)

		last_run = Date.now()
		if (f.__prev === f.value) return
		if (run_scheduled && !force) return

		run_scheduled = true
		function sync_method() {

			//only sync when field hasn't changed for at least {frequency} ms.
			const synced_recently = Date.now() - last_run < frequency
			if ((f.__prev === f.value) || (synced_recently && !force)) {
				setTimeout(sync_method, frequency)
				return
			}

			f.__prev = f.value

			if (typeof method.then === 'function') {
				last_run = Date.now()
				run_scheduled = false
				method()
			}
			else {
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

$.wipe = (field, value = '') => {
	$(field).__prev = $(field).value = value
}

$.all = name => document.getElementsByName(name)

$._EDITORS = {}
$.editor = id => {
	return $._EDITORS[id]
}
$.editor.new = field => {
	const id = (typeof field === 'string') ? field : (field.id || '---')
	$._EDITORS[id] = new SimpleMDE({
		element: $(field),
		autoDownloadFontAwesome: false,
	})
}
$.editor.del = id => delete $._EDITORS[id]

//Pull in a dark overlay, drawing the user's focus to a specific element.
let IS_FOCUSING = false
$.focus = (field, bounds = { left: 0, right: 0, top: 0, bottom: 0 }, padding = 10) => {
	if (!$(field)) {
		console.warn(`Unable to focus on "${field}": no element exists with the given ID or name.`)
		return
	}

	function setFocus() {
		if (!IS_FOCUSING) return

		const rect = $(field).getBoundingClientRect()
		const overlay = document.querySelector('.dark-overlay')

		const left = Math.floor(rect.left - padding - (bounds.left || 0))
		const right = Math.floor(rect.right + padding + (bounds.right || 0))
		const top = Math.floor(rect.top - padding - (bounds.top || 0))
		const bottom = Math.floor(rect.bottom + padding + (bounds.bottom || 0))

		const polygon = `0% 0%, 0% 100%, ${left}px 100%, ${left}px ${top}px, ${right}px ${top}px, ${right}px ${bottom}px, ${left}px ${bottom}px, ${left}px 100%, 100% 100%, 100% 0%`
		_.css.set_var('--focus-overlay', polygon)

		if (IS_FOCUSING) {
			setTimeout(setFocus, 20)
		}
	}

	IS_FOCUSING = false
	setTimeout(() => {
		IS_FOCUSING = true
		setFocus()
	}, 20)
}

$.focus.message = message => {
	const field = $('dark-overlay-text')

	if (field.innerHTML) {
		$.blink(field, true)
		if (message) {
			setTimeout(() => {
				field.innerHTML = message
			}, 300)
		}
	} else if (message) {
		$.hide(field)
		field.innerHTML = message
		$.show(field)
	}
}

$.unfocus = () => {
	IS_FOCUSING = false
	_.css.set_var('--focus-overlay', '')
	$.hide('dark-overlay-text', true)
}


//Update globals $ (fields) and _ (screen)
window.$ = $
window._ = _
