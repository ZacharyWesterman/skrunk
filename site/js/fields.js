import Validate from './fields/validate.js'
import Enforce from './fields/enforce.js'
import Template from './fields/template.js'
import Modal from './fields/modal.js'
import Events from './fields/events.js'
import Control from './fields/control.js'

var _ = Template
_.modal = Modal

_.css = {
	vars: () => document?.styleSheets[document.styleSheets.length-1]?.cssRules[0]?.styleSheet?.rules[0]?.style || [],
	set_var: (name, value) => document.querySelector(':root').style.setProperty(name, value.trim()),
	get_var: name => getComputedStyle(document.querySelector(':root')).getPropertyValue(name).trim(),
}

//Field control and validation
var $ = field => (typeof field === 'object') ? field : document.getElementById(field)
$.val = id => $(id).value
$.set = (id, value) => {
	$(id).value = value
	$(id).prevValue = value
}
$.toggle_expand = id => $(id).classList.toggle('expanded')

$.show = (id, fade = true) => {
	$(id).style.display = ''
	setTimeout(() => {
		$(id).classList.add('fade')
		$(id).classList.remove('hidden')
		$(id).classList.add('visible')
	}, 50)
}
$.hide = (id, fade = false) => {
	var classes = $(id).classList
	classes.toggle('fade', fade)
	classes.remove('visible')
	classes.add('hidden')
	if (fade)
		setTimeout(() => $(id).style.display = 'none', 300)
	else
		$(id).style.display = 'none'
}
$.toggle = (id, state, fade = true) => {
	if (state === undefined) state = $(id).classList.contains('hidden')

	const func = state ? $.show : $.hide
	func(id, fade)
}

$.validate = Validate
$.enforce = Enforce
$.on = Events
$.next = Control.next
$.prev = Control.prev

$.bind = function(field, method, frequency = 500, run_on_start = false)
{
	if (run_on_start) method()

	let last_run = Date.now()
	let run_scheduled = false

	$(field).addEventListener('keyup', () =>
	{
		last_run = Date.now()
		if (run_scheduled) return

		run_scheduled = true
		function sync_method()
		{
			//only sync when field hasn't changed for at least {frequency} ms.
			if (Date.now() - last_run < frequency)
			{
				setTimeout(sync_method, frequency)
				return
			}

			if (typeof method.then === 'function')
			{
				method().then(() => {
					run_scheduled = false
					last_run = Date.now()
				})
			}
			else
			{
				method()
				run_scheduled = false
				last_run = Date.now()
			}
		}

		setTimeout(sync_method, frequency)
	})
}

//Update globals $ (fields) and _ (screen)
window.$ = $
window._ = _
