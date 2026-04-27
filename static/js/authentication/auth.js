class Auth {
	constructor() {

		this.baseAPIUrl = "http://localhost:8000/api";

		this.refreshToken = localStorage.getItem("refreshToken");
		this.accessToken = localStorage.getItem("accessToken");


	}

	async login(username, password) {
		let data = await this.getToken(username, password)
		return data

	}
	async fetchPost(url, body, headers = {}) {

		const response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				...headers,
			},
			body: body
		})

		return response


	}
	async fetchGET(url, body, headers = {}) {

		const response = await fetch(url, {
			method: "GET",
			headers: {
				...headers,
			},
		})

		return response


	}

	async getToken(username, password) {
		const tokenUrl = `${this.baseAPIUrl}/token/`;

		const body = JSON.stringify({
			"email": username,
			"password": password
		})
		try {
			const response = await this.fetchPost(tokenUrl, body)
			console.log(response)
			if (!response.ok) {

				return {
					"ok": false,
					"data": response.json()
				}
			}
			const data = await response.json()
			this.setToken(data.access, data.refresh)


			return {
				"ok": true,
			}
		} catch (error) {
			return {
				"ok": false,
			}

		}


	}

	async setToken(accessToken, refreshToken) {
		this.refreshToken = refreshToken;
		this.accessToken = accessToken;
		localStorage.setItem("refreshToken", refreshToken);
		localStorage.setItem("accessToken", accessToken);

	}
	async setAccessToken(accessToken) {
		this.accessToken = accessToken;
		localStorage.setItem("accessToken", accessToken);

	}
	async refreshAccessToken() {
		const refreshUrl = `${this.baseAPIUrl}/token/refresh/`;

		const body = JSON.stringify({
			"refresh": this.refreshToken
		})
		try {
			const response = await this.fetchPost(refreshUrl, body)

			if (!response.ok) {
				console.log(response)
				throw new Error('Token refresh failed');
			}
			const data = await response.json()
			this.setAccessToken(data.access)
			return true


		} catch (error) {
			this.logout()
			return false

		}
	}
	async authenticatedRequest(url, body, fetchType = "POST") {
		let fetchObject = this.fetchPost
		if (fetchType == "GET") {

			fetchObject = this.fetchGET
		}

		let headers = {
			"Authorization": `Bearer ${this.accessToken}`
		}

		let response = await fetchObject(url, body, headers)
		if (response.status === 401) {
			const refreshed = await this.refreshAccessToken();

			if (refreshed) {
				headers = {
					"Authorization": `Bearer ${this.accessToken}`
				}
				response = await fetchObject(url, body, headers)

			} else {
				this.logout()
				throw new Error('Session expired');
			}
		}

		return response
	}
	async logout() {
		if (this.refreshToken) {
			try {
				const url = `${this.baseAPIUrl}/account/logout/`
				const response = this.authenticatedRequest(url, null)

			} catch (error) {
				console.log("logout error", error)
			}
		}
		this.clearTokens()
		window.location.href = "account/login/"
	}

	async clearTokens() {
		this.accessToken = null
		this.refreshToken = null
		localStorage.removeItem("accessToken")
		localStorage.removeItem("refreshToken")

	}
}