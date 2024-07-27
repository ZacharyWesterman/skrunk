export default async (config, field) => {
	const date_format = environment.mobile ? date.short : date.output
	const users = await api(`{ listUsers (restrict: false) { username last_login } }`)

	const style = field.style
	style['max-height'] = '220px'
	style['overflow-y'] = 'scroll'

	let exact = true

	function toggle() {
		const text = users.map(user => {
			const last_login = user.last_login ? (exact ? date_format(user.last_login) : date.elapsed(user.last_login)) : '<span class="disabled">Never</span>'
			return `<tr><td>${user.username}</td><td>${last_login}</tr>`
		}).reduce((a, b) => a + b)

		field.innerHTML = '<table>' + text + '</table>'
		exact = !exact
	}

	field.onclick = toggle
	toggle()
}
