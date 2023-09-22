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

api.get = function(url, use_cache = true) {
	return new Promise((resolve, reject) => {
		//Don't re-fetch urls that are cached
		if (use_cache)
		{
			const cache_data = cache.read(url)
			if (cache_data !== null)
			{
				resolve(cache_data)
				return
			}
		}

		let xhr = new XMLHttpRequest()
		xhr.open('GET', url)
		xhr.onload = () => {
			if (xhr.status >= 200 && xhr.status < 300)
			{
				//Only cache certain file types.
				for (const filetype of ['.html', '.js', '.css', '.dot', '.json'])
				{
					if (url.endsWith(filetype))
					{
						cache.write(url, xhr.response)
						break
					}
				}
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

api.file_prompt = function (contentType = '*', multiple = false, capture = null)
{
	return new Promise((resolve, reject) => {
		let input = document.createElement('input')
		input.type = 'file'
		input.multiple = multiple
		input.accept = contentType
		if (capture) input.capture = capture

		let resolved = false

		input.onchange = _ => {
			resolved = true
			let files = Array.from(input.files)
			resolve(multiple ? files : files[0])
		}

		const callback = () =>
		{
			setTimeout(() => {
				if (!resolved) reject()
				document.removeEventListener('focus', callback, true)
			}, 100)
		}

		input.click()

		setTimeout(() => {
			document.addEventListener('focus', callback, true)
		}, 50)
	})
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
				resolve(JSON.parse(xhr.responseText))
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

/**
 * Write relevant application variables to site cookies.
 */
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

/**
 * Delete all cookies for this site.
 */
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

/**
 * Read site cookies and set related application variables.
 */
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

/**
 * Hash a password in-browser.
 * @param {string} password The plaintext password to hash.
 * @returns {string} A SHA-512 hash of the given text.
 */
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

/**
 * Log out of the application and go back to the login page.
 */
api.logout = function()
{
	api.__auto_refresh = false
	api.login_token = null
	api.write_cookies()
	window.location.href = '/'
}

/**
 * Helper function for easily fetching the text of an HTML snippet.
 * @param {string} name The base name of the snippet to fetch.
 * @returns {string} The text contents of the snippet.
 */
api.snippit = async name =>
{
	return await api.get(`/html/snippit/${name}.html`)
}

/**
 * Fetch all site data in the background.
 */
api.preload = async () =>
{
	if (!cache.enabled) return

	const resources = await api.get_json('/config/sitemap.json')

	for (const i of resources.js) import(i)
	for (const i of resources.html) api.get(i)
	for (const i of resources.dot) api.get(i)
	for (const i of resources.json) api.get(i)

	query.require('users').then(query.users.list)
}

/**
 * Methods for handling browser data caching.
 */
let cache = {
	enabled: true,

	__data: {},

	/**
	 * Write data to the browser cache based on configured cache settings.
	 * @param {string} name An ID identifying the cached data.
	 * @param {string} data The data to cache.
	 */
	write: function(name, data)
	{
		if (cache.enabled)
			cache.__data[name] = data
	},

	/**
	 * Read data from the browser cache based on configured cache settings.
	 * @param {string} name An ID identifying the cached data.
	 * @returns {(string|null)} The cached data for the given name, if it exists. Null otherwise.
	 */
	read: function(name)
	{
		return cache.enabled ? (cache.__data[name] || null) : null
	},

	/**
	 * Remove data from the browser cache.
	 * @param {string} name An ID identifying the cached data.
	 */
	remove: function(name)
	{
		delete cache.__data[name]
	},

	/**
	 * Delete all cached data.
	 */
	clear: function()
	{
		cache.data = {}
	},
}
