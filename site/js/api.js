const api = {
	login_token : undefined,

	call : async function(query_string, variables=null)
	{
		const query_data = {
			'query' : query_string,
			'variables': variables,
		}

		return new Promise(resolve => {
			this.__request(query_data, resolve)
		})
	},

	authenticate : async function(username, password)
	{
		var self = this

		return new Promise(resolve => {
			self.__hash(password).then(hashed_pass => {
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
	},

	set_cookies : function() {
		document.cookie = 'Authorization=' + this.login_token + ';SameSite=Lax'
	},

	read_cookies : function() {
		if (!document.cookie) return

		document.cookie.split(';').forEach(cookie => {
			const parts = cookie.split('=', 2)
			const name = parts[0].trim()
			const value = parts[1].trim()

			switch(name)
			{
				case 'Authorization':
					this.login_token = value
					break;
			}
		});
	},

	__hash : async function(password)
	{
		const data = new TextEncoder().encode(password)
		const buffer = await crypto.subtle.digest('SHA-512', data)
		const array = Array.from(new Uint8Array(buffer))
		const hex = array.map(b => b.toString(16).padStart(2,'0')).join('')
		return btoa(hex)
	},

	__request : function(request_json, callback)
	{
		var url = '/api'
		var xhr = new XMLHttpRequest()
		xhr.open('POST', url, true)

		xhr.setRequestHeader('Content-Type', 'application/json')
		xhr.send(JSON.stringify(request_json))

		xhr.onreadystatechange = function()
		{
			if (this.readyState === XMLHttpRequest.DONE && typeof callback === 'function')
			{
				if (this.status === 200)
					callback(JSON.parse(this.responseText))
				else
					throw 'RESPONSE ' + this.status + ' ' + this.statusText
			}
		}
	},
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
* When navigating to a url in this domain, be sure to keep any auth headers.
*/
function navigate(url)
{
	var xhr = new XMLHttpRequest()
	xhr.open('GET', url, true)
	xhr.send()
	xhr.onreadystatechange = function()
	{
		if (this.readyState === XMLHttpRequest.DONE)
		{
			document.write(this.responseText)
		}
	}
}
