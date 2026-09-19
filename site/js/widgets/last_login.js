export default async (config, field) => {
	const date_format = environment.mobile ? date.short : date.output
	const is_admin = SelfUserData.perms.includes('admin')

	let users = await api(`{ listUsers (restrict: ${is_admin ? 'false' : 'true'}) { username last_login } }`)
	if (!is_admin) {
		users = users.filter(i => i.username === api.username)
	}

	let sorting = 'username'
	let reverse = false
	let exact = true

	field.innerText = is_admin ? 'Sort by ' : ''
	const button = document.createElement('button')
	button.className = 'button'
	button.style.marginBottom = '10px'
	button.innerText = 'Username'
	if (is_admin) {
		field.appendChild(button)
	}

	const button2 = document.createElement('button')
	button2.className = 'button'
	button2.style.marginLeft = '10px'
	button2.innerText = 'Ascending'
	if (is_admin) {
		field.appendChild(button2)
	}

	const body = document.createElement('div')
	field.appendChild(body)

	const style = body.style
	style['max-height'] = '220px'
	style['overflow-y'] = 'scroll'

	const border = 'style="padding-left: 2px; border-left: 2px solid var(--suppress-text);"'

	function build() {
		const do_sort = (a, b) => {
			if (sorting === 'last_login') {
				if (!a[sorting]) return 1
				if (!b[sorting]) return -1
				return new Date(b[sorting]) - new Date(a[sorting])
			}
			return a[sorting].localeCompare(b[sorting])
		}
		const do_reverse_sort = (a, b) => {
			if (sorting === 'last_login') {
				if (!a[sorting]) return -1
				if (!b[sorting]) return 1
				return new Date(a[sorting]) - new Date(b[sorting])
			}
			return b[sorting].localeCompare(a[sorting])
		}
		users.sort(reverse ? do_reverse_sort : do_sort)

		const text = users.map(user => {
			const last_login = user.last_login ? (exact ? date_format(user.last_login) : date.elapsed(user.last_login)) : '<span class="suppress">Never</span>'
			return `<tr><td>${user.username}</td><td ${border}>${last_login}</tr>`
		}).reduce((a, b) => a + b)

		body.innerHTML = `<table cellspacing=0>
			<tr><th>Username</th><th ${border}>Last Login</th></tr>
			${text}
		</table>`
	}

	function toggle() {
		exact = !exact
		build()
	}

	button.onclick = () => {
		sorting = sorting === 'username' ? 'last_login' : 'username'
		button.innerText = sorting === 'username' ? 'Username' : 'Last Login'
		build()
	}

	button2.onclick = () => {
		reverse = !reverse
		button2.innerText = reverse ? 'Descending' : 'Ascending'
		build()
	}

	body.onclick = toggle
	build()
}
