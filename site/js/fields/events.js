export default {
	enter: (field, action) => {
		register(field, action, 13)
	},

	escape: (field, action) => {
		//TODO
	},

	detach: {
		enter: (field) => {
			unregister(field, 13)
		},

		escape: (field) => {
			//TODO
		},
	}
}

function register(field, action, keyCode)
{
	if (!field.listenedKeys)
	{
		field.listenedKeys = {}
		field.eventListener = event => {
			for (var i in field.listenedKeys)
			{
				if (event.keyCode == i)
				{
					field.listenedKeys[i](field)
				}
			}
		}
		field.addEventListener('keydown', field.eventListener)
	}

	field.listenedKeys[keyCode] = action
}

function unregister(field, keyCode)
{
	if (field.listenedKeys && field.listenedKeys[keyCode])
	{
		delete field.listenedKeys[keyCode]
		if (Object.keys(field.listenedKeys).length === 0)
		{
			field.removeEventListener('keydown', field.eventListener)
			delete field.listenedKeys
			delete field.eventListener
		}
	}
}
