export default async (config, field) => {
	const date_format = environment.mobile ? date.short : date.output

	const users = (await api(`{ listUsers (restrict: false) { username last_login } }`))
		.map(user => {
			const last_login = user.last_login ? date_format(user.last_login) : '<span class="disabled">Never</span>'
			return `<tr><td>${user.username}</td><td>${last_login}</tr>`
		})


	const style = field.style
	style['max-height'] = '220px'
	style['overflow-y'] = 'scroll'
	field.innerHTML = '<table>' + users.reduce((a, b) => a + b) + '</table>'
}
