class ChatClient {
	constructor(token, roomName, currentUserId) {
		this.currentUserId = currentUserId
		this.token = token;
		this.roomName = roomName
		this.ws = null;
		this.isConnected = false;
		this.connect();
	}

	connect() {
		const url = `ws://${window.location.host}/ws/chat/${this.roomName}/?token=${this.token}`;
		try {
			this.ws = new WebSocket(url)
			this.ws.onopen = () => {
				console.log('✅ WebSocket connected');
				this.isConnected = true;
			}
			this.ws.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data)

					this.handleMessage(data)

				} catch (error) {
					console.log('Failed to parse message:', error)
				}
			}
			this.ws.onclose = (event) => {
				console.log(`❌ WebSocket closed: ${event.code} - ${event.reason}`);
				this.isConnected = false;
			}
			this.ws.onerror = (error) => {
				console.error('WebSocket error:', error);
			}
		} catch (error) {
			console.error('Failed to create WebSocket:', error);
		}

	}

	sendMessage(message, conversationId) {
		if (!this.isConnected || !this.ws || this.ws.readyState != WebSocket.OPEN) {
			console.warn('Cannot send message: WebSocket not connected');
			return false
		}
		try {
			this.ws.send(JSON.stringify({
				"message": message,
				"timestamp": new Date().toISOString(),
				"conversationId": conversationId
			}))
		} catch (error) {
			console.error('Failed to send message:', error);
			return false;
		}
	}

	handleMessage(data) {
		const localDate = new Date(data.created_at)
		const message = data.message
		const messagesContainer = document.getElementById("messagesContainer");
		const hour = localDate.getHours();
		const minute = localDate.getMinutes();
		const timeWithLeadingZeros = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;

		if (conversationId == data.conversationId) {

			const msg = `
	    <div class="message ${data.user_id === this.currentUserId ? 'outgoing' : 'incoming'}">
	      <div class="message-sender">${data.username}</div>
	      <div class="bubble">${message}
	        <div class="message-time">${timeWithLeadingZeros}</div>
	      </div>
	    </div>`
			messagesContainer.insertAdjacentHTML("beforeend", msg)
			if (data.user_id === this.currentUserId) {
				messagesContainer.scrollTop = messagesContainer.scrollHeight;

			}

		}
		const chatPreview = document.querySelector(`.chat-item[data-id="${data.conversationId}"] .chat-preview`);
		chatPreview.innerText = message;
	}


	disconcect() {
		if (this.ws) {
			this.ws.close(1000, "User disconnected");
			this.ws = null;
		};
		this.isConnected = false;
	}
}