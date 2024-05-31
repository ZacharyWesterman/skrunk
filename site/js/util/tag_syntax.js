function lexer(src) {
	const types = [
		[/^(and\b|or\b|not\b|\+|\/|-)/i, 'oper'],
		[/^(eq|lt|gt|le|ge|equals?|exact(ly)?|min(imum)?|max(imum)?|fewer|greater|below|above)\b/i, 'func'],
		[/^"(\\"|[^"])*"/, 'str'],
		[/^[a-zA-Z0-9_\.]+/, 'str'],
		[/^\*/, 'wild'],
	]

	let tokens = []
	while (src) {
		let matched = false
		for (const type of types) {
			const m = type[0].exec(src)
			if (m) {
				const text = m[0]
				src = src.substring(text.length)
				tokens.push([text, type[1]])
				matched = true
				break
			}
		}

		if (!matched) {
			const text = src.substring(0, 1)
			src = src.substring(text.length)
			tokens.push([text, null])
		}
	}

	return tokens
}

function render(tokens) {
	return tokens.map(token => {
		return token.length > 1 ? `<span class="${token[1]}">${token[0]}</span>` : token[0]
	}).join('')
}

window.tag_highlight = function (src) {
	const tokens = lexer(src)
	return render(tokens)
}
