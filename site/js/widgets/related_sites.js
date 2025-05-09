export default async (config, field) => {
	const related_sites = ((await api(`{ getConfig(name: "related_sites") }`)) || '[]')
		.split('\n')
		.map(i => {
			try {
				if (i.trim() === '') return null
				const info = JSON.parse(i)
				if (!info) return null
				return {
					url: info[0],
					title: info[1],
					module: info[2],
				}
			} catch (e) {
				console.error('Error parsing related site config:', e)
				return {
					url: '#',
					title: i,
				}
			}
		})
		.filter(i => i !== null)
		.filter(i => !i.module || !SelfUserData.disabled_modules.includes(i.module))

	if (related_sites.length === 0) {
		$.hide(field.parentElement)
		return
	}

	field.innerHTML = related_sites.map(i => `<div style="text-align: center;">
		<a href="${i.url}" target="_blank" class="related_site">${i.title}</a><br>
	</div>`).join(' ')
}
