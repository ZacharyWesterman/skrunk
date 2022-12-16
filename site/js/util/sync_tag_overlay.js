window.sync_tag_overlay = async function(input, output)
{
	const oper = 'blue'
	const func = 'orange'
	const strn = 'green'

	var text = input.value
	text = text.replace(/"(\\"|[^"])*"/g, `<span style="color:${strn}">$&</span>`)
	text = text.replace(/(?<![><"])(?!and)(?!or)(?![&|])\b\w+\b(?![><="])/g, `<span style="color:${strn}">$&</span>`)
	text = text.replace(/\band\b|\bor\b|&|\|/g, `<span style="color:${oper}">$&</span>`)
	text = text.replace(/\b(eq|lt|le|gt|ge)\b/g, `<span style="color:${func}">$&</span>`)

	output.innerHTML = text
}

window.unload.push(() => {
	delete window.sync_tag_overlay
})
