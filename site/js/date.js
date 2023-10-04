window.date = {
	//Precision formats
	YEARS: 'year',
	MONTHS: 'month',
	WEEKS: 'week',
	DAYS: 'day',
	HOURS: 'hour',
	MINUTES: 'minute',
	SECONDS: 'second',
	MILLISECONDS: 'millisecond',

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
	 * @param {boolean} exact If true, output the exact difference (down to precision level). Otherwise output only highest non-zero difference.
	 * @param {string} precision The level of precision to show in the diff. See possible values at top.
	 * @param {boolean} include_zero Whether to include zero-diffs in the output.
	 * @returns {string} The elapsed time between the date and now.
	 */
	elapsed: function(date_obj, exact = false, precision = date.SECOND, include_zero = false)
	{
		let from = (typeof date_obj === 'string') ? new Date(date_obj) : date_obj
		let to = new Date()

		const direction = (to - from >= 0) ? 'ago' : 'in'
		if (direction === 'in') from = [to, to = from][0] //swap from/to to keep diff positive

		let output = []
		const diff = method => to[method]() - from[method]()

		const diffs = {
			year: diff('getFullYear'),
			month: diff('getMonth'),
			week: Math.floor(diff('getDate') / 7),
			day: (exact && (precision !== date.WEEKS)) ? diff('getDate') : (diff('getDate') % 7),
			hour: diff('getHours'),
			minute: diff('getMinutes'),
			second: diff('getSeconds'),
			millisecond: diff('getMilliseconds'),
		}

		const list = ['year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'millisecond']

		//Make sure that all diffs are positive
		const ratio = {
			month: ['year', 12],
			week: ['month', Math.ceil(date.months.days[to.getMonth()] / 7)],
			day: (exact && (precision !== date.WEEKS)) ? ['month', date.months.days[to.getMonth()]] : ['week', 7],
			hour: ['day', 24],
			minute: ['hour', 60],
			second: ['minute', 60],
			millisecond: ['second', 1000],
		}

		for (const i of [...list].reverse())
		{
			if (diffs[i] < 0)
			{
				diffs[i] += ratio[i][1]
				diffs[ratio[i][0]] -= 1
			}
		}

		for (const i of list)
		{
			if (diffs[i] || include_zero)
			{
				output.push(diffs[i] + ' ' + i + ((diffs[i] === 1) ? '' : 's'))
				if (!exact && diffs[i]) break
			}
			if (exact && i === precision) break
		}

		if (output.length === 0)
			return 'Just now'
		else
			return (direction === 'ago') ? output.join(', ') + ' ' + direction : direction + ' ' + output.join(', ')
	}
}
