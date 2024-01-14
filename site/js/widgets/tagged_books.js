export default async (config, field) =>
{
	let chart_data = await api(`{countAllUserBooks { owner { username display_name } count }}`)
	chart_data = chart_data.sort((a,b) => b.count - a.count )

	const labels = chart_data.map(i => i.owner.display_name)
	const data = chart_data.map(i => i.count)

	let use_bar = true

	function toggle()
	{
		if (use_bar)
			chart.bar(field, labels, data, true)
		else
			chart.pie(field, labels, data, true)

		use_bar = !use_bar
	}

	field.onclick = toggle
	toggle()
}
