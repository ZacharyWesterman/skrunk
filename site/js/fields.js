import Validate from './fields/validate.js'
import Enforce from './fields/enforce.js'
import Template from './fields/template.js'
import Modal from './fields/modal.js'
import Events from './fields/events.js'
import Control from './fields/control.js'

var _ = Template
_.modal = Modal

_.css = {
	vars: () => document?.styleSheets[0]?.cssRules[0]?.styleSheet?.rules[0]?.style || [],
	set_var: (name, value) => document.querySelector(':root').style.setProperty(name, value),
	get_var: name => getComputedStyle(document.querySelector(':root')).getPropertyValue(name),
}

//Field control and validation
var $ = field => (typeof field === 'object') ? field : document.getElementById(field)
$.val = id => $(id).value
$.toggle_expand = id => $(id).classList.toggle('expanded')

$.validate = Validate
$.enforce = Enforce
$.on = Events
$.next = Control.next
$.prev = Control.prev

//Update globals $ (fields) and _ (screen)
window.$ = $
window._ = _
