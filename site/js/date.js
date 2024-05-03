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
		days: [
			31,
			28,
			31,
			30,
			31,
			30,
			31,
			31,
			30,
			31,
			30,
			31,
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

	from_field: function(field, offset_days = 0)
	{
		const val = $.val(field)
		if (!val) return null
		const parts = val.split('-')
		const y = parts[0]
		const m = parts[1]
		const d = parts[2]

		let dt = new Date('1970-01-01T00:00:00')
		dt.setYear(y)
		dt.setMonth(m-1)
		dt.setDate(parseInt(d) + offset_days)

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

	short: function(date_obj)
	{
		const dt = (typeof date_obj === 'string') ? new Date(date_obj) : date_obj
		const y = dt.getFullYear()
		const m = dt.getMonth()+1
		const d = dt.getDate()
		const h = String(dt.getHours()).padStart(2, '0')
		const n = String(dt.getMinutes()).padStart(2, '0')
		const s = String(dt.getSeconds()).padStart(2, '0')

		return `${y}-${m}-${d} ${h}:${n}`
	},

	/**
	 * Takes a date and returns a human-readable representation of the difference between the date and now
	 *
	 * @param {string|Date} date_obj The date to compare to the current system date.
	 * @returns {string} The elapsed time between the date and now.
	 */
	elapsed: function(date_obj)
	{
		let from = (typeof date_obj === 'string') ? new Date(date_obj) : date_obj
		let to = new Date()

		const direction = (to - from >= 0) ? 'ago' : 'in'
		if (direction === 'in') from = [to, to = from][0] //swap from/to to keep diff positive

		let output = []
		const diff = to - from

		const ratios = [
			[1000 * 60 * 60 * 24 * 365, 'year'],
			[1000 * 60 * 60 * 24 * 30, 'month'],
			[1000 * 60 * 60 * 24 * 7, 'week'],
			[1000 * 60 * 60 * 24, 'day'],
			[1000 * 60 * 60, 'hour'],
			[1000 * 60, 'minute'],
			[5 * 1000, 'second'], //Ignore any timespan shorter than 5 seconds
		]

		for (const ratio of ratios)
		{
			if (diff > ratio[0])
			{
				const amt = Math.floor(diff / ratio[0])
				output.push(amt + ' ' + ratio[1] + (amt === 1 ? '' : 's'))
				break
			}
		}

		if (output.length === 0)
			return 'Just now'
		else
			return (direction === 'ago') ? output.join(', ') + ' ' + direction : direction + ' ' + output.join(', ')
	}
}
