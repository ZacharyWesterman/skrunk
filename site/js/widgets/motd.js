export default async (config, field) => {
	const motd = await api(`{ getRandomMotd {text_html} }`)
	if (!motd) {
		$.hide(field.parentElement)
		return
	}

	field.innerHTML = `<div style="text-align: center;">${motd.text_html}</div>`
}
