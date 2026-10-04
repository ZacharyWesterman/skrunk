export default async (config, field) => {
	const motd = await api(`{ getRandomMotd {text} }`)
	if (!motd) {
		$.hide(field.parentElement)
		return
	}

	field.innerHTML = `<div style="text-align: center;">${motd.text.replace('\n', '<br>')}</div>`
}
