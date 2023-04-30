let errorID = 0

window.show_error_message = function(error)
{
	let errorDOM = document.getElementById('runtime-errors')
	const thisError = 'runtime-error-' + errorID
	errorID += 1

	errorDOM.innerHTML += `<div id="${thisError}">Error in ${error.fileName} line ${error.lineNumber} col ${error.columnNumber}<br>&rarr;&nbsp;&nbsp;${error.message}</div>`
}

window.show_api_errors = function(error)
{
	let errorDOM = document.getElementById('runtime-errors')
	const thisError = 'runtime-error-' + errorID
	errorID += 1

	let html = `<div id="${thisError}">API Error: ${error.status} ${error.statusText}`
	for (const err of error.errors)
	{
		html += `<br>&rarr;&nbsp;&nbsp;${err.message}`
	}
	html += '</div>'
	errorDOM.innerHTML += html
}

window.show_raw_error_message = function(text)
{
	let errorDOM = document.getElementById('runtime-errors')
	const thisError = 'runtime-error-' + errorID
	errorID += 1
	errorDOM.innerHTML += `<div id="${thisError}">${text}</div>`
}

window.clear_error_message = function()
{
	let errorDOM = document.getElementById('runtime-errors')
	errorDOM.innerHTML = ''
	errorID = 0
}

addEventListener('error', window.show_error_message);
