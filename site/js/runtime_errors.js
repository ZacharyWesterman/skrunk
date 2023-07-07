let errorID = 0

window.show_error_message = function(error)
{
	let errorDOM = document.getElementById('runtime-errors')
	const thisError = 'runtime-error-' + errorID
	errorID += 1

	errorDOM.innerHTML += `<div class="runtime-error fade hidden" id="${thisError}">Error in ${error.fileName} line ${error.lineNumber} col ${error.columnNumber}<br>&rarr;&nbsp;&nbsp;${error.message}</div>`
	setTimeout(() => clear_error_message(thisError), 5000)
	$.show(thisError, true)
}

window.show_api_errors = function(error)
{
	let errorDOM = document.getElementById('runtime-errors')
	const thisError = 'runtime-error-' + errorID
	errorID += 1

	let html = `<div class="runtime-error fade hidden" id="${thisError}">API Error: ${error.status} ${error.statusText}`
	for (const err of error.errors)
	{
		const msg = err?.extensions?.exception?.stacktrace || [err.message]
		for (const i of msg)
		{
			html += `<br>&rarr;&nbsp;&nbsp;${i}`
		}
	}
	html += '</div>'
	errorDOM.innerHTML += html
	setTimeout(() => clear_error_message(thisError), 5000)
	$.show(thisError, true)
}

window.show_raw_error_message = function(text)
{
	let errorDOM = document.getElementById('runtime-errors')
	const thisError = 'runtime-error-' + errorID
	errorID += 1
	errorDOM.innerHTML += `<div class="runtime-error fade hidden" id="${thisError}">${text}</div>`
	setTimeout(() => clear_error_message(thisError), 5000)
	$.show(thisError, true)
}

window.clear_error_message = function(thisError)
{
	if (thisError === undefined)
	{
		let errorDOM = document.getElementById('runtime-errors')
		errorDOM.innerHTML = ''
		errorID = 0
	}
	else
	{
		let errorDOM = document.getElementById(thisError)
		$.hide(thisError, true)
	}
}

addEventListener('error', window.show_error_message);
