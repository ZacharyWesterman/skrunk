export default {
	report: async (title, text) =>
	{
		return await api(`
		mutation ($title: String!, $text: String!) {
			reportBug (title: $title, text: $text)
		}`, {
			title: title,
			text: text,
		})
	},
}
