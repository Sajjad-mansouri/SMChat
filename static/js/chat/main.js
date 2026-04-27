const auth = new Auth()

// Drawer logic
const drawer = document.getElementById("drawerMenu"),
  overlayDr = document.getElementById("drawerOverlay"),
  hamburger = document.getElementById("hamburgerBtn");

function openDrawer() {
  drawer.classList.add("open");
  overlayDr.classList.add("active");
}

function closeDrawer() {
  drawer.classList.remove("open");
  overlayDr.classList.remove("active");
}
hamburger.addEventListener("click", openDrawer);
overlayDr.addEventListener("click", closeDrawer);



function openNav() {
  document.querySelectorAll(".nav-pill").forEach(element => {
    element.classList.remove("active")
  })
  event.target.classList.add("active")
  const dataNav = event.target.dataset.nav

  getConversation(dataNav)
}

async function getConversation(dataNav) {
  const container = document.getElementById("chatsList");
  container.innerText = ""
  const response = await auth.authenticatedRequest(`api/conversations/${dataNav}`, null, "GET")
  if (!response.ok) {
    throw new Error("Faild to get groups!")
  }
  const data = await response.json()
  console.log(data)
  data.forEach(item => {
    populateNavConversations(container, item)
  })

}

function populateNavConversations(container, item) {
  const chat = `<div class="chat-item" data-id="${item.id}" data-name="${item.conversation_name}" onclick="openChat()">
        <div class="chat-avatar" data-id="${item.id}" data-name="${item.conversation_name}">
        <img src="${item.conversation_image}">
        </div>
        <div class="chat-info">
          <div class="chat-name">${item.conversation_name}</div>
          <div class="chat-preview">${item.last_message|| ""}</div>
        </div>
      </div>
      `
  container.insertAdjacentHTML("beforeend", chat);
}

getConversation("direct")

let conversationId = null
const activeSockets = {}
let previousConversationId = null
async function openChat() {
  let chatItem = event.target.closest(".chat-item")

  chatItem.classList.add("active-chat")
  previousConversationId = conversationId;
  conversationId = chatItem.dataset.id;
  const response = await auth.authenticatedRequest(`api/conversation/${conversationId}`, null, "GET")
  const data = await response.json()

  document.querySelectorAll(".chat-item").forEach(element => {
    element.classList.remove("active-chat")
  })

  createMessageContainer(data)
  populateConversationMessages(data)
  createSocket(data)
  changeRoomStatus()



}

function createSocket(data) {
  const token = localStorage.getItem('accessToken');
  if (!Object.hasOwn(activeSockets, conversationId)) {
    console.log("create new socket")
    chatSocket = new ChatClient(token, `${conversationId}`, data.current_user)
    activeSockets[conversationId] = chatSocket
  } else {
    newUserStatus()
  }
}

function newUserStatus() {
  if (Object.hasOwn(activeSockets, conversationId)) {
    console.log("send user status")
    // connect and exit room and again enter use previous socket that created 
    // send status to room
    console.log('active socket****', activeSockets, conversationId)
    ChatSocket = activeSockets[conversationId]
    const messageType = "status_notif"
    const statusType = 'Online'
    const notifTime = "enterRoom"
    chatSocket.statusNotif(conversationId, messageType, statusType, notifTime)

  }

}

function changeRoomStatus() {

  if (previousConversationId != null && previousConversationId != conversationId) {
    console.log("change room", previousConversationId)
    // change user status to offline when go to the other room
    console.log(activeSockets)
    const previousChatSocket = activeSockets[previousConversationId]
    const messageType = "status_notif"
    const statusType = 'Offline'
    const notifTime = "exitRoom"
    previousChatSocket.statusNotif(previousConversationId, messageType, statusType, notifTime)
  }
}

function createMessageContainer(data) {
  const app = document.querySelector(".app")
  let mainContent = document.querySelector(".main-content")
  if (mainContent) {

    mainContent.remove()
  }

  const statusDiv = data.group_type == "direct" ? `<div class="chat-status" id="chatStatus" data-user="${data.profile_id}">Offline</div>` : ""
  mainContent = `
    <main class="main-content">
    <div class="chat-header">
      <div class="chat-title" id="chatTitleClick">
        <div class="header-avatar" id="headerAvatar"></div>
        <div>
          <h2 id="chatName">${data.profile_username}</h2>
          ${statusDiv}
        </div>
      </div>
    </div>
    <div class="messages-container" id="messagesContainer"></div>
    <div id="draftPreviewArea" class="attachment-preview-area" style="display: none;"></div>
    <div class="input-area">
    <div class="input-wrapper"><input type="text" class="msg-input" id="messageInput" placeholder="Type a message...">
    <button class="attach-btn" id="attachFileBtn">
  <svg width = "22" viewBox = "0 0 24 24" fill = "none" stroke = "#475569" >
    <path d = "M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" stroke - width = "1.6" / >
    </svg>
    </button>
    <input type="file" id="fileInput" style="display:none">
    </div>
    <button class="send-button" id="sendBtn" onclick="sendMessage()"><svg width="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
    </svg></button></div>
  </main>
  `
  app.insertAdjacentHTML("beforeend", mainContent)

}

function populateConversationMessages(data) {
  console.log(data)
  const messagesContainer = document.getElementById("messagesContainer")
  data.group_chats.forEach(message => {
    const date = new Date(message.created);
    const hour = date.getHours();
    const minute = date.getMinutes();
    const timeWithLeadingZeros = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    const msg = `
    <div class="message ${message.user.id === data.current_user ? 'outgoing' : 'incoming'}">
      <div class="message-sender">${message.user.username}</div>
      <div class="bubble">${message.text}
        <div class="message-time">${timeWithLeadingZeros}</div>
      </div>
    </div>`
    messagesContainer.insertAdjacentHTML("beforeend", msg)
  })
}

function sendMessage() {
  console.log("send message to ", conversationId)
  const messageValue = document.getElementById("messageInput").value;
  const chatSocket = activeSockets[conversationId]
  const messageType = "message"

  chatSocket.message(messageValue, conversationId, messageType)
}

document.getElementById("createGroupChannelBtn")?.addEventListener("click", () => {
  document.getElementById("drawerMenu")?.classList.remove("open");
  document.getElementById("drawerOverlay")?.classList.remove("active");
  document.getElementById("createModalOverlay")?.classList.add("active");
});
document.getElementById("submitCreateBtn")?.addEventListener("click", async () => {
  const createNameInputValue = document.getElementById("createNameInput").value.trim()
  const createTypeSelectValue = document.getElementById("createTypeSelect").value
  if (createNameInputValue && createTypeSelectValue) {
    const data = await createConversation(createNameInputValue, createTypeSelectValue)
    const container = document.getElementById("chatsList");
    const activeNav = document.querySelector(`.nav-pill.active[data-nav="${data.group_type}"]`);
    if (activeNav) {
      populateNavConversations(container, data)
    }

    document.getElementById("createModalOverlay")?.classList.remove("active");
  }
});
document.getElementById("cancelCreateBtn")?.addEventListener("click", () => document.getElementById("createModalOverlay")?.classList.remove("active"));


async function createConversation(createNameInputValue, createTypeSelectValue) {
  const body = JSON.stringify({
    "name": createNameInputValue,
    "group_type": createTypeSelectValue
  })
  const response = await auth.authenticatedRequest(`api/conversation/create/`, body, "POST")
  return response.json()

}