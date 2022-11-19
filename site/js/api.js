
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
	var self = this

	return new Promise(resolve => {
		self.hash(password).then(hashed_pass => {
			const auth_json = {
				'username': username,
				'password': hashed_pass,
			}

			var url = '/auth'
			var xhr = new XMLHttpRequest()
			xhr.open('POST', url, true)

			xhr.setRequestHeader('Content-Type', 'application/json')
			xhr.send(JSON.stringify(auth_json))

			xhr.onreadystatechange = function()
			{
				if (this.readyState === XMLHttpRequest.DONE && typeof resolve === 'function')
				{
					const response = JSON.parse(this.responseText)
					self.login_token = response.token
					resolve(response.error === undefined)
				}
			}
		})
	})
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

api.write_cookies = function()
{
	var cookie = {
		'Authorization': api.login_token,
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

api.__request = function(request_json, callback)
{
	var url = '/api'
	var xhr = new XMLHttpRequest()
	xhr.open('POST', url, true)

	xhr.setRequestHeader('Content-Type', 'application/json')
	xhr.send(JSON.stringify(request_json))

	xhr.onreadystatechange = function()
	{
		if (xhr.readyState === XMLHttpRequest.DONE && typeof callback === 'function')
		{
			if (xhr.status === 200)
				callback(JSON.parse(xhr.responseText))
			else
				throw 'RESPONSE ' + xhr.status + ' ' + xhr.statusText
		}
	}
}

/*
* Since every request (except auth) MUST have an auth token,
* hijack all http requests and tack on the auth header before sending it on its way again.
*/
XMLHttpRequest.prototype.open = (function(open) {
	return function(method, url, async) {
		open.apply(this, arguments)
		this.setRequestHeader('Authorization', api.login_token)
	}
})(XMLHttpRequest.prototype.open)

/*
* Simple helper function for site navigation.
*/
function navigate(url)
{
	var xhr = new XMLHttpRequest()
	xhr.open('GET', url, true)
	xhr.send()
	xhr.onreadystatechange = function()
	{
		if (xhr.readyState === XMLHttpRequest.DONE)
		{
			if (xhr.status === 200)
			{
				document.head.innerText = ''
				document.body.innerText = ''
				document.write(xhr.responseText)
			}
			else
				throw 'RESPONSE ' + xhr.status + ' ' + xhr.statusText
		}
	}
}
