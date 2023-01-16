window.date = {
	months: {
		abbrev: [
			'Jan',
			'Feb',
			'Mar',
			'Apr',
			'May',
			'Jun',
			'Jul',
			'Aug',
			'Sep',
			'Oct',
			'Nov',
			'Dec',
		],
		full: [
			'January',
			'February',
			'March',
			'April',
			'May',
			'June',
			'July',
			'August',
			'September',
			'October',
			'November',
			'December',
		],
	},

	days: {
		abbrev: [
			'Sun',
			'Mon',
			'Tue',
			'Wed',
			'Thu',
			'Fri',
			'Sat',
		],
		full: [
			'Sunday',
			'Monday',
			'Tuesday',
			'Wednesday',
			'Thursday',
			'Friday',
			'Saturday',
		]
	},

	from_field: function(field)
	{
		const val = $.val(field)
		if (!val) return null
		const parts = val.split('-')
		const y = parts[0]
		const m = parts[1]
		const d = parts[2]

		let dt = new Date()
		dt.setYear(y)
		dt.setMonth(m-1)
		dt.setDate(d)

		return dt
	},

	output: function(date_obj)
	{
		const dt = (typeof date_obj === 'string') ? new Date(date_obj) : date_obj
		const y = dt.getFullYear()
		const m = date.months.abbrev[dt.getMonth()]
		const d = dt.getDate()
		const w = date.days.abbrev[dt.getDay()]
		const h = String(dt.getHours()).padStart(2, '0')
		const n = String(dt.getMinutes()).padStart(2, '0')
		const s = String(dt.getSeconds()).padStart(2, '0')

		return `${w}, ${d} ${m} ${y} at ${h}:${n}:${s}`
	},

	db_output: function(date_obj)
	{
		if (!date_obj) return null
		const dt = (typeof date_obj === 'string') ? new Date(date_obj) : date_obj
		const y = dt.getFullYear()
		const m = String(dt.getMonth() + 1).padStart(2, '0')
		const d = String(dt.getDate()).padStart(2, '0')
		const h = String(dt.getHours()).padStart(2, '0')
		const n = String(dt.getMinutes()).padStart(2, '0')
		const s = String(dt.getSeconds()).padStart(2, '0')

		return `${y}-${m}-${d} ${h}:${n}:${s}`
	},
}
