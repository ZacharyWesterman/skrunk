window.api = async function(query_string, variables = null)
{
	//shorthand for api.call
	const res = await api.call(query_string, variables)
	for (const elem in res.data)
	{
		return res.data[elem]
	}
}

api.login_token = null
api.username = null
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

	api.login_token = 'Bearer ' + response.token
	api.username = username
	return true
}

api.refresh_token = async function()
{
	if (api.login_token === null) return false

	const response = JSON.parse(await api.post_json('/auth', {token: api.login_token}))
	if (response.error) return false

	api.login_token = 'Bearer ' + response.token
	return true
}

api.auto_refresh_token = function(enabled)
{
	function do_auto_refresh()
	{
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
		let xhr = new XMLHttpRequest()
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

api.get_json = async url =>
{
	const result = await api.get(url)
	return JSON.parse(result)
}

api.upload = function(file, progress_handler, auto_unzip = false, tag_list = []) {
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest
		let data = new FormData

		file.unzip = auto_unzip
		data.append('file', file)
		data.append('unzip', auto_unzip)
		data.append('tags', JSON.stringify(tag_list))
		xhr.upload.addEventListener('progress', progress_handler, false)
		xhr.open('POST', '/upload', true)
		xhr.send(data)

		api.upload.xhr.push(xhr)

		xhr.onload = () => {
			api.upload.xhr = []
			if (xhr.status >= 200 && xhr.status < 300)
			{
				resolve(xhr.responseText)
			}
			else
			{
				reject({text: xhr.responseText, status: xhr.status, statusText: xhr.statusText})
			}
		}

		xhr.onerror = () => {
			api.upload.xhr = []
			console.error(xhr)
			reject({text: 'XHR-ON-ERROR', status: xhr.status, statusText: xhr.statusText})
		}
	})
}

api.upload.xhr = []

api.upload.cancel = () => {
	const ret = api.upload.xhr.length > 0

	for (let xhr of api.upload.xhr)
	{
		xhr.abort()
	}
	api.upload.xhr = []

	return ret
}

api.post_json = function(url, json_data) {
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest()
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
	let cookie = {
		'Authorization': api.login_token || null,
		'Username': api.username,
	}

	for (const i of _.css.vars())
	{
		cookie[i] = _.css.get_var(i)
	}

	for (const i in cookie)
	{
		if (cookie[i] === null || cookie[i] === '')
			document.cookie = i + '=; SameSite=Lax; Expires=Thu, 01 Jan 1970 00:00:01 GMT;'
		else
		{
			//All cookies expire after a week
			let expires = new Date()
			expires.setDate(expires.getDate() + 7)

			document.cookie = i + '=' + ((cookie[i] !== null) ? cookie[i] : '') + '; SameSite=Lax; Expires='+expires
		}
	}
}

api.wipe_cookies = function()
{
	let cookie = {
		'Authorization': null,
		'Username': null,
	}
	for (const i of _.css.vars()) cookie[i] = null
	for (const i in cookie)
	{
		document.cookie = i + '=; SameSite=Lax; Expires=Thu, 01 Jan 1970 00:00:01 GMT;'
	}
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
			case 'Username':
				api.username = (value === '') ? null : value
				break;
			case 'SameSite':
				break
			default: //assume everything else is a css var
				_.css.set_var(name, value)
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
		res.errors = JSON.parse(res.response).errors
		show_api_errors(res)
	}
	else
	{
		console.log('Token expired, logging out.')
		api.logout()
	}
}

api.__request = function(request_json, callback)
{
	//show spinner to indicate resources are loading
	$.show($('loader'))

	const url = '/api'
	let xhr = new XMLHttpRequest()
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
			api.handle_query_failure(xhr)
		}

		$.hide($('loader'))
	}

	xhr.onerror = () => {
		api.handle_query_failure(xhr)
		$.hide($('loader'))
	}
}

api.logout = function()
{
	api.__auto_refresh = false
	api.login_token = null
	api.write_cookies()
	window.location.href = '/'
}

api.__snippits = {}
api.snippit = async name =>
{
	//Cache snippits so they're not re-fetched every single time.
	if (api.__snippits[name] === undefined)
	{
		api.__snippits[name] = await api.get(`/html/snippit/${name}.html`)
	}

	return api.__snippits[name]
}