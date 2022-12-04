export default {
	enter: (field, action) => {
		register(field, action, 13)
	},
}

function register(field, action, keyCode)
{
	if (!field.listenedKeys)
	{
		field.listenedKeys = {}
		field.addEventListener('keydown', event => {
			for (var i in field.listenedKeys)
			{
				if (event.keyCode == i)
				{
					field.listenedKeys[i](field)
				}
			}
		})
	}

	field.listenedKeys[keyCode] = action
}
