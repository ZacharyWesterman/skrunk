export default async (config, field) =>
{
	let chart_data = await api(`{countAllUserBooks { owner { username display_name } count }}`)
	chart_data = chart_data.sort((a,b) => b.count - a.count )

	await chart.bar(field, chart_data.map(i => i.owner.display_name), chart_data.map(i => i.count), true)
}
