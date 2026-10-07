export default (field_name) => {
	return new Promise(resolve => {
		const page = environment.get_param('page') ?? 'home'

		api.get_json(`/config/tutorials/${page}${field_name ? '/' + field_name : ''}.json`).then(data => {
			data = data.reverse()

			function next_tut_info() {
				const action = data.pop()
				if (!action) {
					document.removeEventListener('click', next_tut_info)
					$.unfocus()
					resolve()
					return
				}

				const field = document.querySelector(action.selector)
				if (!field || field.style.display === 'none') {
					// If for some reason the desired tutorial field isn't available,
					// just skip to the next tutorial page.
					next_tut_info()
					return
				}

				$.focus(field)
				$.focus.message(`<p>${action.message}</p><i class="emphasis">Click anywhere to ${data.length ? 'continue' : 'exit'}...</i>`)
			}
			document.addEventListener('click', next_tut_info)
			next_tut_info()
		})
	})
}
