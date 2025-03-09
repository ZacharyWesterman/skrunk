let __resize_listeners = []

export default {
	tab: (field, action) => register(field, action, 9),
	enter: (field, action) => register(field, action, 13),
	escape: (field, action) => register(field, action, 27),

	blur: (field, action) => {
		register(field, action, 9)
		register(field, action, 13)
	},

	hover: (field, action) => {
		field.eventListener = event => {
			action(event)
		}
		field.addEventListener('mouseover', field.eventListener)
	},

	resize: action => {
		const listener = event => {
			action(event)
		}
		__resize_listeners.push(listener)

		window.addEventListener('resize', listener)
	},

	detach: {
		tab: field => unregister(field, 9),
		enter: field => unregister(field, 13),
		escape: field => unregister(field, 27),
		hover: field => field.removeEventListener('mouseover', field.eventListener),
		resize: () => {
			for (const i of __resize_listeners) {
				window.removeEventListener('resize', i)
			}
			__resize_listeners = []
		},
	},
}

function register(field, action, keyCode) {
	if (!field.listenedKeys) {
		field.listenedKeys = {}
		field.eventListener = event => {
			for (const i in field.listenedKeys) {
				if (event.keyCode == i) {
					field.listenedKeys[i](field)
					event.stopPropagation()
					event.preventDefault()
				}
			}
		}
		field.addEventListener('keydown', field.eventListener)
	}

	field.listenedKeys[keyCode] = action
}

function unregister(field, keyCode) {
	if (field.listenedKeys && field.listenedKeys[keyCode]) {
		delete field.listenedKeys[keyCode]
		if (Object.keys(field.listenedKeys).length === 0) {
			field.removeEventListener('keydown', field.eventListener)
			delete field.listenedKeys
			delete field.eventListener
		}
	}
}
