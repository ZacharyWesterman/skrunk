
/**
 * Call the GraphQL API.
 * @param {string} query_string The appropriate query or mutation string.
 * @param {object} variables Any variables that need to be passed in for queries or mutations.
 * @returns {object} The API response per the schema.
 */
window.api = function(query_string, variables = null)
{
	const query_data = {
		'query' : query_string,
		'variables': variables,
	}

	return new Promise((resolve, reject) => {
		//show spinner to indicate resources are loading
		$.show($('loader'))

		fetch('/api', {
			method: 'POST',
			mode: 'cors',
			cache: 'no-cache',
			credentials: 'same-origin',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': api.login_token,
			},
			body: JSON.stringify(query_data),
		}).then(res => {
			if (res.status >= 200 && res.status < 300 && res.ok)
			{
				res.json().then(response => {
					for (const elem in response.data)
					{
						resolve(response.data[elem])
						break
					}
				})
			}
			else
			{
				api.handle_query_failure(res)
				reject(res.responseText)
			}

			$.hide('loader')

		}).catch(res => {
			api.handle_query_failure(res)
			reject(res.responseText)
			$.hide('loader')
		})
	})
}

/**
 * Keep track of the logged in user's session token.
 */
api.login_token = null

/**
 * Keep track of the logged in user's username.
 */
api.username = null

/**
 * Login to the server, generating a session token on success.
 * @param {string} username The username.
 * @param {string} password The plaintext password (this gets hashed).
 * @returns {boolean} Whether the login was successful.
 */
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

/**
 * Refresh the session token, generating a new one.
 * @returns {boolean} Whether the token refreshed successfully.
 */
api.refresh_token = async function()
{
	if (api.login_token === null) return false

	const response = JSON.parse(await api.post_json('/auth', {token: api.login_token}))
	if (response.error) return false

	api.login_token = 'Bearer ' + response.token
	return true
}

/**
 * Keep track of whether the session token is being automatically refreshed.
 */
api.__auto_refresh = false

/**
 * Specify whether session token automatically refreshes while the page is open.
 * @param {boolean} enabled Whether to enable/disable auto-refresh.
 */
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

/**
 * Check if the current session token is valid.
 * @returns {boolean} Whether the current session token is valid.
 */
api.verify_token = async function()
{
	if (api.login_token === null) return false
	const response = JSON.parse(await api.post_json('/auth/verify', {token: api.login_token}))

	return response.valid
}

/**
 * Get data from the server.
 * @param {string} url The path to set GET request.
 * @param {boolean} use_cache Use cached static data if it exists.
 * @returns {string} The response text from the server.
 */
api.get = function(url, use_cache = true) {
	url = url.replace(/^\//, '')

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

		fetch(url).then(res => {
			if (res.status >= 200 && res.status < 300 && res.ok)
			{
				//Only cache certain file types.
				for (const filetype of ['.html', '.js', '.css', '.dot', '.json'])
				{
					if (url.endsWith(filetype))
					{
						res.text().then(text => {
							cache.write(url, text)
							resolve(text)
						})
						return
					}
				}

				res.text().then(resolve)
			}
		})
	})
}

/**
 * Get data from the server, parsing the response as JSON.
 * @param {string} url
 * @returns {any} The response from the server.
 */
api.get_json = async url =>
{
	const result = await api.get(url)
	return JSON.parse(result)
}

/**
 * Launch a file upload dialog.
 * If the user cancels, this throws an exception.
 *
 * @param {string} contentType Values like "image/png,video/*" or "image/*", etc.
 * @param {boolean} multiple Allow selecting multiple files.
 * @param {string} capture If specified, can be values like "camera".
 * @returns {File} The uploaded file, if one was uploaded. An array of files if the multiple flag is true.
 */
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

/**
 * Upload a file to the server.
 *
 * @param {File} file
 * @param {function({loaded:number, total:number}):void} progress_handler A callback to run when the progress bar updates.
 * @param {boolean} auto_unzip Automatically unpack any zip files once upload completes.
 * @param {string[]} tag_list Tags to attach to the file on upload.
 * @param {boolean} hidden Keep uploaded file hidden from all users except the uploader.
 * @returns {any} The JSON response from the server.
 */
api.upload = function(file, progress_handler, auto_unzip = false, tag_list = [], hidden = false, ephemeral = false) {
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest
		let data = new FormData

		api.upload.canceled = false

		file.unzip = auto_unzip
		data.append('file', file)
		data.append('unzip', auto_unzip)
		data.append('hidden', hidden)
		data.append('ephemeral', ephemeral)
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

/**
 * Keep track of files currently being uploaded.
 */
api.upload.xhr = []

/**
 * Cancel any pending file uploads.
 *
 * @returns {boolean} Whether any file uploads were canceled.
 */
api.upload.cancel = () => {
	const ret = api.upload.xhr.length > 0
	api.upload.canceled = true

	for (let xhr of api.upload.xhr)
	{
		xhr.abort()
	}
	api.upload.xhr = []

	return ret
}

/**
 * Send a POST request to the server.
 *
 * @param {string} url The path to POST to.
 * @param {any} json_data Data to send.
 * @returns {string} The response text from the POST request.
 */
api.post_json = async function(url, json_data)
{
	const res = await fetch(url, {
		method: 'POST',
		mode: 'cors',
		cache: 'no-cache',
		credentials: 'same-origin',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': api.login_token,
		},
		body: JSON.stringify(json_data),
	})

	if (res.status >= 200 && res.status < 300 && res.ok)
	{
		return await res.text()
	}
	else
	{
		throw {status: res.status, statusText: res.statusText}
	}
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

/**
 * When a query fails, check why, and log the failure.
 * @param {object} res Result from api call.
 */
api.handle_query_failure = async function(res)
{
	if (await api.verify_token())
	{
		res.errors = (await res.json()).errors
		console.error('API ERROR:', res.errors)
		show_api_errors(res)
	}
	else
	{
		console.log('Token expired, logging out.')
		api.logout()
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
api.snippit = async (name, url_only = false) =>
{
	if (url_only) return `/html/snippit/${name}.html`
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
