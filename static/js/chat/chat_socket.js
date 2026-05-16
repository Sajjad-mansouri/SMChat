class ChatClient {
	constructor(token, roomName, currentUserId, initMessage) {
		this.currentUserId = currentUserId
		this.token = token;
		this.roomName = roomName
		this.initMessage = initMessage
		this.ws = null;
		this.isConnected = false;
		this.CHUNK_SIZE = 1 * 1024;
		this.connect();
	}

	connect() {
		const url = `ws://${window.location.host}/ws/chat/${this.roomName}/?token=${this.token}`;
		try {
			this.ws = new WebSocket(url)
			this.ws.onopen = () => {

				this.isConnected = true;
				const statusType = "Online";
				const notifTime = "enterRoom";
				const messageType = "status_notif"
				this.statusNotif(this.roomName, messageType, statusType, notifTime)
				if (this.initMessage) {
					document.querySelector(".chat-status").setAttribute("data-user", conversationId)
					this.message(this.initMessage, conversationId)
				}
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

	message(message, conversationId, messageType = "message", replyingTo = null, file = null) {
		const replyTo = replyingTo ? replyingTo.id : null
		const messageObject = {
			"messageType": messageType,
			"message": message,
			"conversationId": conversationId,
			"replyTo": replyTo
		}
		if (file) {

			this.sendFile(messageObject, file)
		} else {

			this.send(messageObject)
		}

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
	sleep(ms) {
		// just for simulate delay in real world
		return new Promise(resolve => setTimeout(resolve, ms));
	}
	async sendFile(messageObject, file) {
		this.isCancelled = false
		this.fileInfo = {
			name: file.name,
			size: file.size,
			content_type: file.type,
		}
		this.ws.send(JSON.stringify({
			position: "start",
			...this.fileInfo,
			...messageObject,
		}));

		this.offset = 0;
		while (this.offset < file.size) {


			if (this.isCancelled) {
				this.ws.send(JSON.stringify({
					"cancel": true,
					"message_type": "cancellation",
					"conversationId": messageObject["conversationId"]

				}));
				break
			}

			const chunck = file.slice(this.offset, this.offset + this.CHUNK_SIZE);
			const buffer = await chunck.arrayBuffer();
			this.ws.send(buffer)
			this.offset += this.CHUNK_SIZE

		}
		if (!this.isCancelled) {

			this.ws.send(JSON.stringify({
				"position": "end",
				...this.fileInfo,
				...messageObject
			}))
		}
	}

	handleMessage(data) {

		if (data.messageType == "status_notif") {

			this.changeChatStatus(data)


		} else {
			if (!Object.hasOwn(data, "progress")) {
				this.addMessageToContainer(data)
				this.changePreviewText(data)
			} else if (data["position"] == "start") {
				cancelDraft()
				this.createProgressBar(data)
			} else {
				this.updateProgressBar(data["percentage"])

			}

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
			let replyHtml;
			if (data.message_type == "cancellation") {
				return
			}
			if (data.reply_to) {
				replyHtml = `
		          <div class="reply-preview">
		            <div class="reply-sender">↳ ${data.reply_to.user_username}</div>
		            <div class="reply-content">${escapeHtml(data.reply_to.text.substring(0, 80))}${data.reply_to.text.length > 80 ? '...' : ''}</div>
		          </div>
		        `;
			} else {
				replyHtml = ""
			}
			let messageContent;
			if (data.image) {
				messageContent = `
      <img src="${data.image}" class="chat-image">
      <div class="caption-text">${escapeHtml(data.message)}</div>
      `

			} else if (data.file) {
				messageContent = `
      <a href = "${data.file}"
      download = "${data.file.split('/').pop()}"
      class = "file-attachment" >  

      <svg width = "20"viewBox = "0 0 24 24"fill = "none"
      stroke = "currentColor" > <path d = "M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM13 2v7h7" stroke - width = "1.6" /> 
      </svg> ${data.file.split('/').pop()}
      </a>
      <div class="caption-text">${escapeHtml(data.message)}</div>
      `
			} else {
				messageContent = data.message
			}
			const msg = `
				    <div class="message ${data.sender_id === this.currentUserId ? 'outgoing' : 'incoming'}">
				        <div class="message-sender">${data.sender_username}</div>
						<div class = "bubble" > 
						${replyHtml}
						${messageContent}
				        <div class="message-time">${timeWithLeadingZeros}</div>
				        
  <div class="message-actions">
     <button class="action-icon-btn reply-msg-btn" data-id="${data.msg_id}" data-sender="${data.sender_id === this.currentUserId ? 'You' : data.sender_id}" data-preview="${getMessagePreview(data).replace(/"/g, '&quot;')}" onclick="reply()">
      <svg width="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M10 11h4M12 9v4"/></svg>
    </button>
  </div>
				      </div>
				    </div>`
			messagesContainer.insertAdjacentHTML("beforeend", msg)
			if (data.sender_id === this.currentUserId) {
				messagesContainer.scrollTop = messagesContainer.scrollHeight;

			}
		}


	}

	changePreviewText(data) {
		const chatPreview = document.querySelector(`.chat-item[data-conversation-id="${data.conversationId}"] .chat-preview`);
		chatPreview.innerText = data.message;
	}

	changeChatStatus(data) {


		if (data.sender_id != this.currentUserId) {

			const chatStatus = document.querySelector(`.chat-status[data-conversation-id="${data.conversationId}"]`);


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

	createProgressBar(data, type = "image", file = {
		name: "best book"
	}) {

		const toast = document.createElement('div');
		toast.className = 'upload-progress-toast';
		const fileNameShort = file.name.length > 28 ? file.name.slice(0, 25) + '...' : file.name;
		toast.innerHTML = `
        <div class="progress-toast-header">
          <span>📤 Uploading ${type === 'image' ? 'image' : 'file'}</span>
          <button class="cancel-upload" id="cancelUploadBtn" >✕</button>
        </div>
        <div class="progress-bar-bg"><div class="progress-fill" id="uploadFill" style="width:0%"></div></div>
        <div class="progress-stats">
          <span id="uploadPercent">0%</span>
        </div>
      `;
		document.body.appendChild(toast);
		document.getElementById("cancelUploadBtn").addEventListener("click", this.cancelUploading.bind(this), {
			once: true
		})

	}
	cancelUploading() {

		this.isCancelled = true

		document.querySelector(".upload-progress-toast").remove()
	}

	updateProgressBar(percent) {
		const toast = document.querySelector(".upload-progress-toast")
		const fill = toast.querySelector('#uploadFill');
		const percentSpan = toast.querySelector('#uploadPercent');
		if (fill) fill.style.width = percent + '%';
		if (percentSpan) percentSpan.innerText = Math.floor(percent) + '%';
		if (percent == 100) {
			toast.remove();
		}
	}
}

function escapeHtml(str) {
	if (!str) return '';
	return String(str).replace(/[&<>]/g, function(m) {
		if (m === '&') return '&amp;';
		if (m === '<') return '&lt;';
		if (m === '>') return '&gt;';
		return m;
	});
}