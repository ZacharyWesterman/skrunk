export default {
	next: field => {
		var sibling = field.nextElementSibling
		while (sibling) {
			if (['INPUT', 'BUTTON'].includes(sibling.tagName))
			{
				sibling.focus()
				break
			}

			sibling = sibling.nextElementSibling
		}
	},

	prev: field => {
		var sibling = field.previousElementSibling
		while (sibling) {
			if (['INPUT', 'BUTTON'].includes(sibling.tagName))
			{
				sibling.focus()
				break
			}

			sibling = sibling.previousElementSibling
		}
	},
}
