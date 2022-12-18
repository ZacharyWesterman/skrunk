const OPER = /^(and\b|or\b|&|\|)/i
const FUNC = /^(eq|lt|le|gt|ge)\b/i
const STR1 = /^"(\\"|[^"])*"/
const STR2 = /^\w+\b/
const Cursor = '<span class="cursor">|</span>'

window.sync_tag_overlay = async function(input, output)
{
	const oper = 'blue'
	const func = 'orange'
	const strn = 'green'

	if (!input.value.length)
	{
		output.innerHTML = ''
		return
	}

	const position = input.selectionStart
	var text = ''
	for (var i = 0; i < input.value.length; ++i)
	{
		const in_text = input.value.substring(i)

		function operate(pattern, color)
		{
			const match = in_text.match(pattern)
			if (match)
			{
				var t = match[0]
				const dif = position - i
				i += t.length - 1
				if ((dif >= 0) && (dif < t.length)) t = t.substring(0, dif) + Cursor + t.substring(dif)
				text += `<span style="color:${color}">${t}</span>`
			}
			return match ? true : false
		}

		if (operate(OPER, oper)) continue
		if (operate(FUNC, func)) continue
		if (operate(STR1, strn)) continue
		if (operate(STR2, strn)) continue

		if (position === i) text += Cursor
		text += (in_text[0] === ' ') ? '&nbsp;' : in_text[0]
	}
	if (position >= input.value.length) text += Cursor

	output.innerHTML = text
}

window.unload.push(() => {
	delete window.sync_tag_overlay
})
