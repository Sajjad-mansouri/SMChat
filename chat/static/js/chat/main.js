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

function openChat() {



  document.querySelectorAll(".chat-item").forEach(element => {
    element.classList.remove("active-chat")
  })
  chatItem.classList.add("active-chat")
}


function openNav() {
  const dataNav = event.target.dataset.nav

  getConversation(dataNav)
}

async function getConversation(dataNav) {
  const container = document.getElementById("chatsList");
  container.innerText = ""
  const response = await auth.authenticatedRequest(`api/conversation/${dataNav}`, null, "GET")
  if (!response.ok) {
    throw new Error("Faild to get groups!")
  }
  const data = await response.json()
  console.log(data)
  data.forEach(item => {
    const chat = `<div class="chat-item" data-id="${item.id}" data-name="${item.conversation_name}" onclick="openChat()">
        <div class="chat-avatar" data-id="${item.id}" data-name="${item.conversation_name}">
        <img src="${item.conversation_image}">
        </div>
        <div class="chat-info">
          <div class="chat-name">${item.conversation_name}</div>
          <div class="chat-preview">${item.last_message}</div>
        </div>
      </div>
      `
    container.insertAdjacentHTML("beforeend", chat);
  })

}

getConversation("direct")