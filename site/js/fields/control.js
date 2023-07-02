export default {
	next: field => {
		let sibling = field.nextElementSibling
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
		let sibling = field.previousElementSibling
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
