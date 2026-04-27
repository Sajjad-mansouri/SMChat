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
				const statusType = "Online";
				const notifTime = "enterRoom";
				const messageType = "status_notif"
				this.statusNotif(this.roomName, messageType, statusType, notifTime)
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

	message(message, conversationId, messageType = "message") {

		const messageObject = {
			"messageType": messageType,
			"message": message,
			"conversationId": conversationId,
		}

		this.send(messageObject)
	}

	statusNotif(conversationId, messageType = "message", statusType = "Online", notifTime = "enterRoom") {
		if (status == "Online") {

			this.roomName = conversationId
		}
		const messageObject = {
			"messageType": messageType,
			"conversationId": conversationId,
			"statusType": statusType,
			"notifTime": notifTime,
		}
		this.send(messageObject)
	}

	send(messageObject) {
		if (!this.isConnected || !this.ws || this.ws.readyState != WebSocket.OPEN) {
			console.warn('Cannot send message: WebSocket not connected');
			return false
		}
		try {
			this.ws.send(JSON.stringify(messageObject))

		} catch (error) {
			console.error('Failed to send message:', error);
			return false;
		}
	}

	handleMessage(data) {
		if (data.messageType == "status_notif") {
			this.changeChatStatus(data)


		} else {
			this.addMessageToContainer(data)
			this.changePreviewText(data)

		}
	}



	addMessageToContainer(data) {
		const localDate = new Date(data.created_at)
		const message = data.message
		const messagesContainer = document.getElementById("messagesContainer");
		const hour = localDate.getHours();
		const minute = localDate.getMinutes();
		const timeWithLeadingZeros = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
		if (this.roomName == data.conversationId) {

			const msg = `
				    <div class="message ${data.sender_id === this.currentUserId ? 'outgoing' : 'incoming'}">
				        <div class="message-sender">${data.sender_username}</div>
						<div class = "bubble" > ${message}
				        <div class="message-time">${timeWithLeadingZeros}</div>
				      </div>
				    </div>`
			messagesContainer.insertAdjacentHTML("beforeend", msg)
			if (data.sender_id === this.currentUserId) {
				messagesContainer.scrollTop = messagesContainer.scrollHeight;

			}
		}


	}

	changePreviewText(data) {
		const chatPreview = document.querySelector(`.chat-item[data-id="${data.conversationId}"] .chat-preview`);
		chatPreview.innerText = data.message;
	}

	changeChatStatus(data) {

		if (data.sender_id != this.currentUserId) {
			const chatStatus = document.querySelector(`.chat-status[data-user="${data.sender_id}"]`);

			if (data.statusType == "Online") {
				// should change if multiple member exist 
				chatStatus.innerText = "Online"
				if (data.notifTime == "enterRoom") {

					this.sendBackStatus(data)
				}

			} else if (data.statusType == "Offline") {
				chatStatus.innerText = "Offline"
			}
		}


	}
	sendBackStatus(data) {
		// only send status to message that enter not for all message
		// user that enter room send i am online who are online?
		this.ws.send(JSON.stringify({
			"send_back": true,
			"messageType": "status_notif",
			"conversationId": this.roomName,
			"statusType": "Online",


		}))


	}
	disconcect() {
		if (this.ws) {
			this.ws.close(1000, "User disconnected");
			this.ws = null;
		};
		this.isConnected = false;
	}
}