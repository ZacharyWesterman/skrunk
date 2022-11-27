import Validate from './fields/validate.js'
import Enforce from './fields/enforce.js'
import Template from './fields/template.js'
import Modal from './fields/modal.js'

var _ = Template
_.modal = Modal

//Field control and validation
var $ = field => (typeof field === 'object') ? field : document.getElementById(field)
$.val = id => $(id).value
$.toggle_expand = id => $(id).classList.toggle('expanded')

$.validate = Validate
$.enforce = Enforce

//Update globals $ (fields) and _ (screen)
window.$ = $
window._ = _
