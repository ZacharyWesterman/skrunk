const api = {
	call : async function(query_string, variables=null)
	{
		var query_data = {
			'query' : query_string,
			'variables': variables,
		}

		return new Promise(resolve => {
			this.__request(query_data, resolve)
		})
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
				callback(JSON.parse(this.responseText))
			}
		}
	},
}
