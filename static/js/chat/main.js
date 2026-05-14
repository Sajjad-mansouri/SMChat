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



function openNav(Nav = null, callback = null) {
  document.querySelectorAll(".nav-pill").forEach(element => {
    element.classList.remove("hidden")
    element.classList.remove("active")
  })
  document.querySelector(".search-nav").classList.add("hidden")
  let dataNav;
  if (Nav) {
    document.querySelector(`.nav-pill[data-nav="${Nav}"`).classList.add("active")
    dataNav = Nav;
  } else {
    event.target.classList.add("active")
    dataNav = event.target.dataset.nav
  }

  getConversation(dataNav, callback)
}

async function getConversation(dataNav, callback = null) {
  const container = document.getElementById("chatsList");
  container.innerText = ""
  const response = await auth.authenticatedRequest(`api/conversations/${dataNav}`, null, "GET")
  if (!response.ok) {
    throw new Error("Faild to get groups!")
  }
  const data = await response.json()
  data.forEach(item => {
    populateNavConversations(container, item)
  })

  if (callback) callback();
}

function populateNavConversations(container, item) {

  const userId = item.group_type == "direct" ? `data-user-id="${item.id}"` : ""
  const blockedBadgeSpan = item.blocklist_id != null ? '<span class="blocked-chip">Blocked</span>' : "";
  const chat = `
      <div class="chat-item" data-conversation-id="${item.conversation_id}" data-type="${item.group_type}" 
      data-bio="${item.bio}" data-name="${item.conversation_name}"  ${userId} onclick="openChat()">
        <div class="chat-avatar" >
        <img src="${item.conversation_image}">
        </div>
        <div class="chat-info">
          <div class="chat-name">${item.conversation_name} ${blockedBadgeSpan}</div>
          <div class="chat-preview">${item.last_message|| ""}</div>
        </div>
      </div>
      `
  container.insertAdjacentHTML("beforeend", chat);
}

getConversation("direct")
let replyingTo = null;
let conversationId = null
const activeSockets = {}
let previousConversationId = null
const currentUser = document.getElementById("drawerUsername").dataset.currentUser

async function openChat(chatId = null) {

  let chatItem
  if (chatId) {

    chatItem = document.querySelector(`.chat-item[data-conversation-id="${chatId}"]`);


  } else {

    chatItem = event.target.closest(".chat-item")
  }


  previousConversationId = conversationId;
  conversationId = chatItem.dataset.conversationId;
  const userId = chatItem.dataset.userId
  const conversationType = chatItem.dataset.type;


  const userIdData = conversationType == "direct" && userId != "undefined" ? userId : null

  let url;
  if (userIdData != null) {
    url = `api/conversation/${conversationType}/user/${userIdData}`;
  } else {
    url = `api/conversation/${conversationType}/${conversationId}`;
  }

  const response = await auth.authenticatedRequest(url, null, "GET")
  if (response.ok) {

    const data = await response.json()
    console.log('data', data)

    document.querySelectorAll(".chat-item").forEach(element => {
      element.classList.remove("active-chat")
    })
    chatItem.classList.add("active-chat")

    createMessageContainer(data)

    if (userId == "undefined" | userId == undefined) {
      populateConversationMessages(data)
      createSocket(data)
      changeRoomStatus()
    }
  } else if (response.status == 403 && ["group", "channel"].includes(conversationType)) {
    const conversationName = chatItem.dataset.name;
    const conversationBio = chatItem.dataset.bio
    createJoinLink(conversationId, conversationName, conversationType, conversationBio)

  }

}

function createSocket(data, initMessage = null) {
  const token = localStorage.getItem('accessToken');
  if (!Object.hasOwn(activeSockets, conversationId)) {
    chatSocket = new ChatClient(token, `${conversationId}`, data.current_user, initMessage)
    activeSockets[conversationId] = chatSocket
  } else {
    newUserStatus()
  }
}

function newUserStatus() {
  if (Object.hasOwn(activeSockets, conversationId)) {
    // connect and exit room and again enter use previous socket that created 
    // send status to room
    ChatSocket = activeSockets[conversationId]
    const messageType = "status_notif"
    const statusType = 'Online'
    const notifTime = "enterRoom"
    chatSocket.statusNotif(conversationId, messageType, statusType, notifTime)

  }

}

function changeRoomStatus() {

  if (previousConversationId != null && previousConversationId != conversationId) {
    // change user status to offline when go to the other room
    const previousChatSocket = activeSockets[previousConversationId]
    const messageType = "status_notif"
    const statusType = 'Offline'
    const notifTime = "exitRoom"
    previousChatSocket.statusNotif(previousConversationId, messageType, statusType, notifTime)
    previousConversationId = conversationId;
  }
}

function createMessageContainer(data) {
  const app = document.querySelector(".app")
  let mainContent = document.querySelector(".main-content")
  if (mainContent) {

    mainContent.remove()
  }
  let conversationId;
  let userData;
  if (!Object.hasOwn(data, "conversation_id")) {
    conversationId = ""
    userData = `data-user-id="${data.id}"`
  } else {
    conversationId = data.conversation_id
    userData = ""
  }
  const disabled = data.blocklist_id != null ? `disabled=''` : ""
  let inputElements = `
    <div id="replyBar" class="reply-bar" style="display: none;">
      <div class="reply-bar-info">
        <div class="reply-bar-sender" id="replyBarSender">Replying to...</div>
        <div class="reply-bar-text" id="replyBarText"></div>
      </div>
      <button class="cancel-reply-btn" id="cancelReplyBtn" onclick="hideReplyBar()">
        <svg width="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
      </button>
    </div>
    <div id="draftPreviewArea" class="attachment-preview-area" style="display: none;"></div>
    <div class="input-area">
    <div class="input-wrapper"><input type="text" class="msg-input" id="messageInput" placeholder="Type a message..." ${disabled}>
    <button class="attach-btn" id="attachFileBtn" ${disabled} onclick="attachFileBtn()">
  <svg width = "22" viewBox = "0 0 24 24" fill = "none" stroke = "#475569" >
    <path d = "M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" stroke - width = "1.6" / >
    </svg>
    </button>
    <input type="file" id="fileInput" style="display:none" >
    </div>
    <button class="send-button" id="sendBtn" onclick="sendMessage()" ${disabled}><svg width="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
    </svg></button></div>
  `
  let userInputElement = "";
  if (data.group_type == "channel") {
    console.log(data.created_by, currentUser, typeof data.created_by, typeof currentUser, data.created_by == currentUser)
    if (data.created_by == currentUser) {
      userInputElement = inputElements
    }
  } else {
    userInputElement = inputElements
  }
  let statusDiv;
  if (data.group_type == "direct") {
    let blocklistClass = "";
    let statusText = "Offline";
    if (data.blocklist_id != null) {
      blocklistClass = "blocked-status";
      statusText = "🔴 Blocked";
    }
    statusDiv = `<div class="chat-status ${blocklistClass}" id="chatStatus" data-group-type="${data.group_type}"data-conversation-id="${conversationId}" ${userData}>${statusText}</div>`
  } else {
    statusDiv = ""
  }



  mainContent = `
    <main class="main-content">
    <div class="chat-header" onclick="openUserProfile()" >
      <div class="chat-title" id="chatTitleClick">
        <div class="header-avatar" id="headerAvatar"><img  src="${data.conversation_image}"></div>
        <div>
          <h2 id="chatName" data-conversation-id="${conversationId}" ${userData} data-group-type="${data.group_type}"data-conversation-id="${conversationId}">${data.conversation_name}</h2>
          ${statusDiv}
        </div>
      </div>
    </div>
    <div class="messages-container" id="messagesContainer">
    </div>
    ${userInputElement}
  </main>
  `
  app.insertAdjacentHTML("beforeend", mainContent)

}

function createJoinLink(conversationId, conversationName, conversationType, conversationBio) {
  const app = document.querySelector(".app")
  let mainContent = document.querySelector(".main-content")
  if (mainContent) {

    mainContent.remove()
  }

  mainContent = `
    <main class="main-content">
    <div id="joinPromptContainer" style="height: 100%;">
      <div class="join-container">
        <div class="join-icon" id="joinIcon">📢</div>
        <div class="join-title" id="joinTitle">${conversationType}:${conversationName}</div>
        <div class="join-description" id="joinDescription">${conversationBio||""}</div>
        <button class="join-button" id="joinButton" data-id="${conversationId}" onclick="joinConversation(${conversationId}, '${conversationType}') ">
          <svg width="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
          Join ${conversationName}
        </button>
      </div>
    </div>
  </main>
  `
  app.insertAdjacentHTML("beforeend", mainContent)
}

async function joinConversation(conversationId, conversationType) {

  const body = JSON.stringify({
    "conversation": conversationId,
  })
  const response = await auth.authenticatedRequest(`api/membership/add/`, body, "POST")
  if (response.ok) {
    const data = await response.json()
    if (data.accepted) {
      openNav(conversationType, () => {
        openChat(conversationId)
      })

    } else {
      document.getElementById("joinButton").innerHTML = `
  <svg width="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M5 2h14M5 22h14M5 2v4c0 4 3 6 7 6s7-2 7-6V2M5 22v-4c0-4 3-6 7-6s7 2 7 6v4"></path>
  </svg>
  Awaiting Approval
      `
    }
  }
}

function populateConversationMessages(data) {
  const messagesContainer = document.getElementById("messagesContainer")

  data.group_chats.forEach(message => {
    const date = new Date(message.created);
    const hour = date.getHours();
    const minute = date.getMinutes();
    const timeWithLeadingZeros = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    let replyHtml;
    let messageContent;
    if (message.image) {
      messageContent = `
      <img src="${message.image}" class="chat-image">
      <div class="caption-text">${escapeHtml(message.text)}</div>
      `

    } else if (message.file) {
      messageContent = `
      <a href = "${message.file}"
      download = "${message.file.split('/').pop()}"
      class = "file-attachment" >  

      <svg width = "20"viewBox = "0 0 24 24"fill = "none"
      stroke = "currentColor" > <path d = "M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM13 2v7h7" stroke - width = "1.6" /> 
      </svg> ${message.file.split('/').pop()}
      </a>
      <div class="caption-text">${escapeHtml(message.text)}</div>
      `
    } else {
      messageContent = message.text
    }
    if (message.reply_to) {
      replyHtml = `
          <div class="reply-preview">
            <div class="reply-sender">↳ ${message.reply_to.user_username}</div>
            <div class="reply-content">${escapeHtml(message.reply_to.text.substring(0, 80))}${message.reply_to.text.length > 80 ? '...' : ''}</div>
          </div>
        `;
    } else {
      replyHtml = ""
    }
    const msg = `
    <div class="message ${message.user.id === data.current_user ? 'outgoing' : 'incoming'}">
      <div class="message-sender">${message.user.username}</div>
      <div class="bubble">
      ${replyHtml}
      ${messageContent}
        <div class="message-time">${timeWithLeadingZeros}</div>
      <div class="message-actions">
        <button class="action-icon-btn reply-msg-btn" data-id="${message.id}" data-sender="${message.user.id === data.current_user ? 'You' : message.user.username}" data-preview="${getMessagePreview(message).replace(/"/g, '&quot;')}" onclick="reply()">
          <svg width="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M10 11h4M12 9v4"/></svg>
        </button>
      </div>
      </div>

    </div>`
    messagesContainer.insertAdjacentHTML("beforeend", msg)
  })

  if (data.blocklist_id != null) {

    message = `<div class="system-message"><div class="system-bubble">⚠️ You have Blocked ${data.conversation_name} <button class="unblock-suggestion-btn" style="background:#dc2626;" onclick="blockConversation('${data.conversation_name}',${data.conversation_id}, ${data.id}, ${data.blocklist_id}, false)">Unblock User</button></div></div>`
    messagesContainer.insertAdjacentHTML("beforeend", message)
  }

}

async function sendMessage() {

  const messageValue = document.getElementById("messageInput").value;
  if (conversationId == "undefined") {
    // if we dont have previous chat with this user first create conversation and add users to it then create socker
    const userId = document.getElementById("chatName").dataset.userId
    const response = await createConversation("", "direct", "", "private", userId)
    if (response.ok) {
      const data = await response.json()
      conversationId = data.conversation_id
      openNav("direct", () => {
        createSocket(data, messageValue)

        document.querySelector(`.chat-item[data-conversation-id="${conversationId}"]`).classList.add("active-chat")
      })

    }
  } else {
    const chatSocket = activeSockets[conversationId]
    const messageType = "message"

    chatSocket.message(messageValue, conversationId, messageType, replyingTo)

  }
  hideReplyBar()
  document.getElementById("messageInput").value = ""
}

document.getElementById("createGroupChannelBtn")?.addEventListener("click", () => {
  document.getElementById("drawerMenu")?.classList.remove("open");
  document.getElementById("drawerOverlay")?.classList.remove("active");
  document.getElementById("createModalOverlay")?.classList.add("active");
});
document.getElementById("submitCreateBtn")?.addEventListener("click", async () => {
  const createNameInputValue = document.getElementById("createNameInput").value.trim()

  const createBioInputValue = document.getElementById("createBioInput").value.trim()

  const createStatusSelectValue = document.getElementById("createStatusSelect").value
  const createTypeSelectValue = document.getElementById("createTypeSelect").value

  if (createNameInputValue && createTypeSelectValue) {
    const response = await createConversation(createNameInputValue, createTypeSelectValue, createBioInputValue, createStatusSelectValue)
    const data = await response.json()
    const container = document.getElementById("chatsList");
    const activeNav = document.querySelector(`.nav-pill.active[data-nav="${data.group_type}"]`);
    if (activeNav) {
      populateNavConversations(container, data)
    }

    document.getElementById("createModalOverlay")?.classList.remove("active");
  }
});
document.getElementById("cancelCreateBtn")?.addEventListener("click", () => document.getElementById("createModalOverlay")?.classList.remove("active"));


async function createConversation(createNameInputValue, createTypeSelectValue, createBioInputValue, createStatusSelectValue, userId = null) {
  const body = JSON.stringify({
    "name": createNameInputValue,
    "bio": createBioInputValue,
    "status": createStatusSelectValue,
    "group_type": createTypeSelectValue,
    "member_user": userId
  })
  const response = await auth.authenticatedRequest(`api/conversation/create/`, body, "POST")
  return response

}

async function addToMembership() {


}

document.getElementById("globalSearch").addEventListener("input", async (event) => {
  const container = document.getElementById("chatsList");
  container.innerText = ""
  search = event.target.value.trim()

  if (search != "") {

    const response = await auth.authenticatedRequest(`api/search/?search=${search}`, null, "GET")
    const data = await response.json()
    document.querySelectorAll(".nav-pill").forEach(element => {
      element.classList.add("hidden")
    })
    document.querySelector(".search-nav").classList.remove("hidden")
    Object.entries(data).forEach(([key, values]) => {
      values.forEach(value => {
        populateNavConversations(container, value)

      })

    })
  } else {

    openNav("direct")
    let mainContent = document.querySelector(".main-content")
    if (mainContent) {

      mainContent.remove()
    }
  }
})


function getMessagePreview(msg) {

  if (msg.image) return '📷 Photo';
  if (msg.file) return `📎 ${msg.fileName || 'File'}`;
  return msg.text || '';


}

function reply() {
  // Attach reply button events
  event.stopPropagation();
  const btn = event.target.closest(".reply-msg-btn")
  const msgId = btn.dataset.id;
  const senderName = btn.dataset.sender;
  const preview = btn.dataset.preview;
  showReplyBar(msgId, senderName, preview);
}


function showReplyBar(messageId, senderName, previewText) {
  replyingTo = {
    id: messageId,
    senderName,
    previewText
  };

  const bar = document.getElementById('replyBar');
  document.getElementById('replyBarSender').innerText = `Replying to ${senderName}`;
  document.getElementById('replyBarText').innerText = previewText.length > 60 ? previewText.substring(0, 60) + '...' : previewText;
  bar.style.display = 'flex';
}

function hideReplyBar() {
  replyingTo = null;
  document.getElementById('replyBar').style.display = 'none';
}



async function openUserProfile() {
  const modal = document.getElementById("profileModal");
  modal.innerHTML = ""
  const ChatHeader = document.getElementById("chatName");
  const conversationId = ChatHeader.dataset.conversationId;
  const userId = ChatHeader.dataset.userId;
  const conversationType = ChatHeader.dataset.groupType;

  const userIdData = conversationType == "direct" && userId != "undefined" ? userId : null
  if (userIdData != null) {
    url = `api/conversation/${conversationType}/user/${userIdData}/profile/`;
  } else {
    url = `api/conversation/${conversationType}/profile/${conversationId}`;

  }
  const response = await auth.authenticatedRequest(url, null, "GET")
  const data = await response.json()
  const blocklistID = data.blocklist_id
  let changeImageSpan = ""
  let conversationSettingEle = ""

  if (currentUser == data.created_by && conversationType != "direct") {

    changeImageSpan = `<span onclick= "changeConversationAvatar('${conversationType}', ${conversationId})">change</span>`
    conversationSettingEle = `<div ><button class="header-settings-btn" id="chatSettingsBtn" onclick="conversationSetting('${conversationId}')">⚙️</button></div>`
  }

  const memberDiv = conversationType == "direct" ? "" : `<div class="profile-modal-members" id="modalMembers">${data.members} subscribers</div>`
  const modalContent = `
  <div class="profile-modal">
    <div class="profile-modal-header">
      <button class="close-modal" id="closeModalBtn" onclick="closeProfileModal()">✕</button>
      <div class="profile-modal-avatar" id="modalAvatar">
        <img id="conversation-img" src="${data.conversation_image}">
        <input type="file" id="avatarUpload" style="display:none" accept="image/*">
        ${changeImageSpan}

      </div>
      <div class="profile-modal-name" id="modalName">${data.conversation_name}</div>
      ${memberDiv}
    </div>
    <div class="profile-modal-body">
      <div class="profile-bio">
        <div class="profile-bio-label">📝 Bio</div>
        <div class="profile-bio-text" id="modalBio">${data.bio}</div>
      </div>
      <div class="profile-actions">
        <button class="message-user-btn" id="messageUserBtn">
          <svg width="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          Send Message
        </button>
        <div style="position: relative;display:flex">
          <button class="three-dots-btn" id="threeDotsBtn" onclick = "openThreeDot()">
            <svg width="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
          </button>

          <div class="dropdown-menu" id="dropdownMenu" >
            <div class="dropdown-item" id="blockUserBtn" onclick="blockConversation('${data.conversation_name}',${data.conversation_id}, ${data.id}, ${data.blocklist_id}, true)">
              <svg width="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><path d="M4 4l16 16"/></svg>
              ${data.blocklist_id!= null ?"UnBlock":"Block"} User
            </div>

          </div>
        </div>
            ${conversationSettingEle}
      </div>
    </div>
  </div>
  `
  modal.innerHTML = modalContent
  modal.classList.add("active");
  document.querySelector('.dropdown-menu').classList.remove('active');
}

// Modal close and dropdown logic
function closeProfileModal() {
  document.getElementById("profileModal").classList.remove("active");

}

document.getElementById("profileModal").addEventListener("click", (e) => {
  if (e.target === document.getElementById("profileModal")) {
    document.getElementById("profileModal").classList.remove("active");
  }
});

// Three dots dropdown
function openThreeDot() {
  event.stopPropagation();
  const dropdownMenu = document.getElementById("dropdownMenu");

  dropdownMenu.classList.toggle("active");

}


document.addEventListener("click", (e) => {
  if (!e.target.closest("#threeDotsBtn") && !e.target.closest("#dropdownMenu")) {
    hideDropDownMenu()
  }
});

function hideDropDownMenu() {
  const dropdownMenu = document.getElementById("dropdownMenu");
  if (dropdownMenu) {

    dropdownMenu.classList.remove("active");
  }

}


async function blockConversation(conversationName, conversationId, userId, blocklistID = null, displayProfile = false) {
  if (blocklistID == null) {
    // Show confirmation modal BEFORE blocking

    showBlockConfirmation(conversationName, "block", async () => {


      // re-render maybe update chat list if needed
      let body
      if (conversationId == undefined) {
        body = JSON.stringify({
          "blocked_user": userId,
        })

      } else {
        body = JSON.stringify({
          "conversation": conversationId,
        })
      }

      const response = await auth.authenticatedRequest(`api/blocklist/toggle/`, body, "POST")
      if (response.ok) {
        hideBlockConfirmation();
        openUserProfile()
        openNav("direct", () => {
          openChat(conversationId)
        })

      }

    });
  } else {
    showBlockConfirmation(conversationName, "unblock", async () => {

      const response = await auth.authenticatedRequest(`api/blocklist/toggle/${blocklistID}/`, "", "DELETE")
      if (response.ok) {
        if (displayProfile) {

          openUserProfile()
        }
        openNav("direct", () => {
          openChat(conversationId)
        })

      }
    })
  }



}


const blockConfirmModal = document.getElementById("blockConfirmModal");
let pendingBlockAction = null; // store the callback for actual block

function showBlockConfirmation(userName, action, onConfirm) {
  const descEl = document.getElementById("confirmBlockDesc");
  const confirmationBtn = document.getElementById("confirmBlockBtn")
  const confirmationTitle = document.querySelector(".confirmation-title")
  let message = "";
  if (action == "block") {
    message = `You are about to block <strong>${escapeHtml(userName)}</strong>. They will no longer be able to message you, and you won't see their messages. You can unblock later from the profile menu.`;
    confirmationBtn.innerText = "Block"
    confirmationTitle.innerText = "Block User?"
  } else {
    message = `You are about to unblock <strong>${escapeHtml(userName)}</strong>. `;
    confirmationBtn.innerText = "UnBlock"
    confirmationTitle.innerText = "UnBlock User?"



  }
  descEl.innerHTML = message
  blockConfirmModal.classList.add("active");
  pendingBlockAction = onConfirm;
}

function hideBlockConfirmation() {
  blockConfirmModal.classList.remove("active");
  pendingBlockAction = null;
}


document.getElementById("cancelBlockBtn").addEventListener("click", hideBlockConfirmation);
document.getElementById("confirmBlockBtn").addEventListener("click", () => {
  if (pendingBlockAction) {
    pendingBlockAction();
  }
  hideBlockConfirmation();
});
blockConfirmModal.addEventListener("click", (e) => {
  if (e.target === blockConfirmModal) hideBlockConfirmation();
});



// file and image upload

function attachFileBtn() {
  document.getElementById("fileInput")?.click()
  document.getElementById("fileInput")?.addEventListener("change", e => {
    handleFileUpload(e.target.files);
    e.target.value = '';
  }, {
    once: true
  });
}


function cancelDraft() {
  pendingDraft = null;
  const area = document.getElementById("draftPreviewArea");
  if (area) {
    area.style.display = "none";
    area.innerHTML = "";
  }
}

function handleFileUpload(files) {
  if (!files.length) return;
  const f = files[0];
  const isImg = f.type.startsWith('image/');
  const reader = new FileReader();
  reader.onload = (e) => {
    pendingDraft = {
      file: f,
    };
    showDraft(f, e.target.result, isImg ? 'image' : 'file', f.name);
  };
  reader.readAsDataURL(f);
}

function showDraft(file, url, type, fileName) {
  const area = document.getElementById("draftPreviewArea");
  if (!area) return;
  area.style.display = "flex";
  area.innerHTML = `<div class="draft-file">${type === 'image' ? `<img src="${url}" style="width:48px;height:48px;">` : `<svg width="32" viewBox="0 0 24 24" fill="none" stroke="#2563eb"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM13 2v7h7"/></svg>`}<div><strong>${fileName}</strong></div><button class="remove-draft" id="removeDraftBtn">✕</button></div><div class="caption-input-area"><input type="text" class="caption-input" id="draftCaption" placeholder="Add caption..."><button id="sendDraftBtn" class="send-draft-btn">Send</button><button id="cancelDraftBtn" class="cancel-draft-btn">Cancel</button></div>`;
  document.getElementById("removeDraftBtn")?.addEventListener("click", cancelDraft);
  document.getElementById("cancelDraftBtn")?.addEventListener("click", cancelDraft);
  document.getElementById("sendDraftBtn")?.addEventListener("click", () => sendMessageWithDraft());
}

async function sendMessageWithDraft() {
  if (pendingDraft) {
    const caption = document.getElementById("draftCaption")?.value || "";
    const d = pendingDraft;

    if (conversationId == "undefined") {
      // if we dont have previous chat with this user first create conversation and add users to it then create socker
      const userId = document.getElementById("chatName").dataset.userId
      const response = await createConversation("", "direct", "", "private", userId)
      if (response.ok) {
        const data = await response.json()
        conversationId = data.conversation_id
        openNav("direct", () => {

          createSocket(data, caption)

          document.querySelector(`.chat-item[data-conversation-id="${conversationId}"]`).classList.add("active-chat")
        })

      }
    } else {

      const chatSocket = activeSockets[conversationId]
      const messageType = "file"


      chatSocket.message(caption, conversationId, messageType, replyingTo, pendingDraft.file)

    }

    document.getElementById('replyBar').style.display = 'none';
  }


}


document.getElementById("logoutBtnDrawer").addEventListener("click", () => {
  auth.logout()
})


async function changeConversationAvatar(conversationType, conversationId) {
  document.getElementById("avatarUpload").click();
  document.getElementById("avatarUpload").addEventListener("change", function() {
    const file = this.files[0]
    const reader = new FileReader();

    const accountAvatarImg = document.getElementById("conversation-img")
    reader.onload = async function(e) {
      const origin = window.location.origin
      formData = new FormData()
      formData.append("image", file)
      formData.append("member_user", currentUser)

      const response = await auth.authenticatedRequest(`${origin}/api/conversation/${conversationId}/update/`, formData, "PATCH", {}, "multipart/form-data")
      const data = await response.json()

      accountAvatarImg.src = e.target.result;

      openNav(conversationType, () => {
        openChat(conversationId)
      })
    }
    reader.readAsDataURL(file)
  }, {
    once: true
  })

}


// settings
let isModalInitialized = false;

async function conversationSetting(conversationId) {
  const settingsModalOverlay = document.getElementById("settingsModalOverlay")
  settingsModalOverlay.classList.add("active")
  addSettingModalCloseListener(settingsModalOverlay)
  const data = await getConversationInfo(conversationId)
  setSettingInputValues(data)
  loadConversationMembers(data)


}

function addSettingModalCloseListener(settingsModalOverlay) {
  const closeBtn = document.getElementById("closeSettingsBtn");
  const cancelSettingsBtn = document.getElementById("cancelSettingsBtn")
  if (!isModalInitialized) {
    // Close button listener
    closeBtn.addEventListener("click", closeSettingsModal);
    cancelSettingsBtn.addEventListener("click", closeSettingsModal);

    // Overlay click listener (close when clicking outside)
    settingsModalOverlay.addEventListener("click", (e) => {
      if (e.target === settingsModalOverlay) {
        closeSettingsModal();
      }
    });

    isModalInitialized = true;
  }
}

async function getConversationInfo(conversationId) {
  const origin = window.location.origin
  const url = origin + `/api/conversation/${conversationId}/setting/`
  const response = await auth.authenticatedRequest(url, null, "GET")
  const data = await response.json()
  return data


}

function setSettingInputValues(data) {
  const settingsSpaceName = document.getElementById("settingsSpaceName")
  settingsSpaceName.value = data.name

  const settingsPrivacy = document.getElementById("settingsPrivacy")
  settingsPrivacy.value = data.status
}

function loadConversationMembers(data) {
  console.log('load member', data)
  const membersList = document.getElementById("membersList");
  const joinRequestsList = document.getElementById("joinRequestsList")

  const accepted = data.members.filter(member => {

    return member.accepted == true
  })

  const requested = data.members.filter(member => {

    return member.accepted == false
  })
  document.getElementById("memberCountBadge").innerText = accepted.length
  document.getElementById("requestsCountBadge").innerText = requested.length

  if (accepted.length === 0) {
    membersList.innerHTML = '<div class="empty-state">No members yet</div>'
  } else {
    membersList.innerHTML = ""

    accepted.forEach(member => {
      console.log(member)
      console.log(currentUser, member.user.id, currentUser == member.user.id)
      console.log(data.created_by, member.user.id, data.created_by == member.user.id)

      isSelf = currentUser == member.user.id
      isCreator = data.created_by == member.user.id
      membersList.insertAdjacentHTML("beforeend", `
        <div class="member-item" data-member="${member.id}">
          <div class="member-info">
            <div class="member-avatar"><img src="${member.user.conversation_image}"></div>
            <div class="member-details">
              <div class="member-name">${member.user.username} ${isCreator ? '👑 Admin' : ''} ${isSelf ? '(You)' : ''}</div>
              <div class="member-role">${isCreator ? 'Creator' : (isSelf ? 'You' : 'Member')}</div>
            </div>
          </div>
          ${(!isCreator && !isSelf ) ? `<button class="remove-member-btn" data-memberid="${member.id}">Remove</button>` : ''}
        </div>
`)
    })

  }

  if (requested.length === 0) {
    joinRequestsList.innerHTML = `<div class="empty-state">✨ No pending join requests</div>`
  } else {
    joinRequestsList.innerHTML = ""
    requested.forEach(member => {
      joinRequestsList.insertAdjacentHTML("beforeend", `
        <div class="request-item">
          <div class="request-info">
            <div class="request-avatar"><img src="${member.user.conversation_image}"></div>
            <div class="member-details">
              <div class="member-name">${member.user.username}</div>
              <div class="member-role">wants to join</div>
            </div>
          </div>
          <button class="accept-request-btn" data-reqid="${member.id}">✓ Accept</button>
        </div>
`)
    })
  }

}

function closeSettingsModal() {
  document.getElementById("settingsModalOverlay").classList.remove("active");

}


document.querySelectorAll(".management-tabs .tab-btn").forEach(element => {

  element.addEventListener("click", () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    element.classList.add("active")

    currentTab = element.dataset.tab;
    document.getElementById('membersTab').classList.remove('active');
    document.getElementById('requestsTab').classList.remove('active');
    if (currentTab === 'members') document.getElementById('membersTab').classList.add('active');
    else document.getElementById('requestsTab').classList.add('active');
  })
})