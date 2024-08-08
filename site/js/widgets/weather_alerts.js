export default async (config, field) => {
	const res = await api(`query ($username: String!) {
		getWeatherAlerts(username: $username, start: 0, count: 1) {
			message
			sent
		}
	}`, {
		username: api.username,
	})

	if (res.length === 0) {
		$.hide(field.parentElement)
		return
	}

	const { sent, message } = { ...res[0] }
	field.innerHTML = `<div class="disabled">${date.elapsed(sent)}</div><p>${message.trim().replaceAll('\n', '<br>')}</p>`
}
