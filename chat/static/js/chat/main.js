const auth = new Auth()

async function getGroup() {
  const response = await auth.authenticatedRequest("api/index/", null, "GET")
  console.log(response)
  if (!response.ok) {
    throw new Error("Faild to get groups!")
  }
  const data = await response.json()
  console.log(data)

}
getGroup()
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