function lexer(src) {
	const types = [
		[/^(and\b|or\b|not\b|&|\||~)/i, 'oper'],
		[/^(eq|lt|le|gt|ge)\b/i, 'func'],
		[/^"(\\"|[^"])*"/, 'str'],
		[/^\w+\b/, 'str'],
	]

	var tokens = []
	while (src)
	{
		var matched = false
		for (var type of types)
		{
			const m = type[0].exec(src)
			if (m)
			{
				const text = m[0]
				src = src.substring(text.length)
				tokens.push([text, type[1]])
				matched = true
				break
			}
		}

		if (!matched)
		{
			const text = src.substring(0, 1)
			src = src.substring(text.length)
			tokens.push([text, null])
		}
	}

	return tokens
}

function render(tokens)
{
	return tokens.map(token => {
		return token.length > 1 ? `<span class="${token[1]}">${token[0]}</span>` : token[0]
	}).join('')
}

window.tag_highlight = function(src)
{
	const tokens = lexer(src)
	return render(tokens)
}

window.unload.push(() => {
	delete window.tag_highlight
})
