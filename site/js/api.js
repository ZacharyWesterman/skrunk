
var api = async function(query_string, variables = null)
{
	//shorthand for api.call
	var res = await api.call(query_string, variables)
	for (var elem in res.data)
	{
		return res.data[elem]
	}
}

api.login_token = null
api.__auto_refresh = false

api.call = async function(query_string, variables = null)
{
	const query_data = {
		'query' : query_string,
		'variables': variables,
	}

	return new Promise(resolve => {
		api.__request(query_data, resolve)
	})
}

api.authenticate = async function(username, password)
{
	const hashed_pass = await api.hash(password)
	const auth_json = {
		'username': username,
		'password': hashed_pass,
	}

	const response = JSON.parse(await api.post_json('/auth', auth_json))
	if (response.error) return false

	api.login_token = response.token
	return true
}

api.refresh_token = async function()
{
	if (api.login_token === null) return false

	const response = JSON.parse(await api.post_json('/auth', {token: api.login_token}))
	if (response.error) return false

	api.login_token = response.token
	return true
}

api.auto_refresh_token = function(enabled)
{
	var do_auto_refresh = () => {
		if (api.login_token === null) return
		if (!api.__auto_refresh) return

		setTimeout(async () => {
			const success = await api.refresh_token()
			if (success)
				do_auto_refresh()
			else
				api.logout()
		}, 3600000) //Try to refresh token every hour
	}

	if (!api.__auto_refresh)
	{
		api.__auto_refresh = enabled
		do_auto_refresh() //don't run function multiple times
	}
	api.__auto_refresh = enabled
}

api.verify_token = async function()
{
	if (api.login_token === null) return false
	const response = JSON.parse(await api.post_json('/auth/verify', {token: api.login_token}))

	return response.valid
}

api.get = function(url) {
	return new Promise((resolve, reject) => {
		var xhr = new XMLHttpRequest()
		xhr.open('GET', url)
		xhr.onload = () => {
			if (xhr.status >= 200 && xhr.status < 300)
			{
				resolve(xhr.response)
			}
			else
			{
				reject({status: xhr.status, statusText: xhr.statusText})
			}
		}

		xhr.onerror = () => {
			reject({status: xhr.status, statusText: xhr.statusText})
		}

		xhr.send()
	})
}

api.post_json = function(url, json_data) {
	return new Promise((resolve, reject) => {
		var xhr = new XMLHttpRequest()
		xhr.open('POST', url, true)
		xhr.setRequestHeader('Content-Type', 'application/json')
		xhr.send(JSON.stringify(json_data))
		xhr.onload = () => {
			if (xhr.status >= 200 && xhr.status < 300)
			{
				resolve(xhr.responseText)
			}
			else
			{
				resolve(xhr.responseText)
			}
		}

		xhr.onerror = () => {
			reject({status: xhr.status, statusText: xhr.statusText})
		}
	})
}

api.write_cookies = function()
{
	var cookie = {
		'Authorization': api.login_token ? ('Bearer ' + api.login_token) : null,
		'SameSite': 'Lax',
	}

	var text = ''
	for (i in cookie)
	{
		text += i + '=' + ((cookie[i] !== null) ? cookie[i] : '') + ';'
	}
	document.cookie = text
}

api.read_cookies = function()
{
	if (!document.cookie) return

	document.cookie.split(';').forEach(cookie => {
		const parts = cookie.split('=', 2)
		const name = parts[0].trim()
		const value = parts[1].trim()

		switch(name)
		{
			case 'Authorization':
				api.login_token = (value === '') ? null : value
				break
		}
	})
}

api.hash = async function(password)
{
	const data = new TextEncoder().encode(password)
	const buffer = await crypto.subtle.digest('SHA-512', data)
	const array = Array.from(new Uint8Array(buffer))
	const hex = array.map(b => b.toString(16).padStart(2,'0')).join('')
	return btoa(hex)
}

api.handle_query_failure = async function(res)
{
	if (await api.verify_token())
	{
		throw 'RESPONSE ' + res.status + ' ' + xhr.statusText
	}
	else
	{
		console.log('Token expired, logging out.')
		api.logout()
	}
}

api.__request = function(request_json, callback)
{
	var url = '/api'
	var xhr = new XMLHttpRequest()
	xhr.open('POST', url, true)

	xhr.setRequestHeader('Content-Type', 'application/json')
	xhr.setRequestHeader('Authorization', api.login_token)
	xhr.send(JSON.stringify(request_json))

	xhr.onload = () => {
		if (xhr.status >= 200 && xhr.status < 300)
		{
			callback(JSON.parse(xhr.responseText))
		}
		else
		{
			api.handle_query_failure({status: xhr.status, statusText: xhr.statusText})
		}
	}

	xhr.onerror = () => {
		api.handle_query_failure({status: xhr.status, statusText: xhr.statusText})
	}
}

api.logout = function()
{
	api.__auto_refresh = false
	api.login_token = null
	api.write_cookies()
	window.location.href = '/'
}

/*
* Simple helper function for site navigation.
*/
async function navigate(url)
{
	await inject(document.all.body, url)
}

/*
* Load content from URL into the given field.
*/
async function inject(field, url)
{
	//Eval script and (if it errors) give more accurate error info.
	function do_script_eval(text, url, replaceUrl)
	{
		try {
			eval(text)
		} catch (error) {
			var stack = error.stack.trim().split('\n')
			stack = stack[stack.length-1].split(':')
			stack[2] = (replaceUrl ? '@' : stack[2]) + url
			stack[3] = error.lineNumber
			stack[4] = error.columnNumber
			if (replaceUrl)
			{
				stack.shift()
				stack.shift()
			}
			error.stack = stack.join(':')
			console.log(error)
		}
	}

	try {
		var res = await api.get(url)
	} catch (error) {
		await api.handle_query_failure(error)
	}

	field.innerHTML = res

	for (var script of field.getElementsByTagName('script'))
	{
		if (script.src.length)
		{
			if (script.attributes.async) //async, so allow more scripts to be loaded
			{
				api.get(script.src).then(res => {
					do_script_eval(res, script.src, true)
				}).catch(error => {
					throw 'RESPONSE ' + error.status + ' ' + error.statusText
				})
			}
			else //load scripts synchronously
			{
				try {
					res = await api.get(script.src)
				} catch (error) {
					throw 'RESPONSE ' + error.status + ' ' + error.statusText
				}
				do_script_eval(res, script.src, true)
			}
		}
		else //eval inline script text
		{
			do_script_eval(script.text, url, false)
		}
	}
}

api.read_cookies()
