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
	set_var: (name, value) => document.querySelector(':root').style.setProperty(name, value),
	get_var: name => getComputedStyle(document.querySelector(':root')).getPropertyValue(name),
}

//Field control and validation
var $ = field => (typeof field === 'object') ? field : document.getElementById(field)
$.val = id => $(id).value
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

$.validate = Validate
$.enforce = Enforce
$.on = Events
$.next = Control.next
$.prev = Control.prev

//Update globals $ (fields) and _ (screen)
window.$ = $
window._ = _
