export default {
	/**
	 * Focus on the field after the given field.
	 * @param {object} field A reference to the current field.
	 */
	next: field => {
		let sibling = field.nextElementSibling
		while (sibling) {
			if (['INPUT', 'BUTTON'].includes(sibling.tagName)) {
				sibling.focus()
				break
			}

			sibling = sibling.nextElementSibling
		}
	},

	/**
	 * Focus on the field before the given field.
	 * @param {object} field A reference to the current field.
	 */
	prev: field => {
		let sibling = field.previousElementSibling
		while (sibling) {
			if (['INPUT', 'BUTTON'].includes(sibling.tagName)) {
				sibling.focus()
				break
			}

			sibling = sibling.previousElementSibling
		}
	},
}
