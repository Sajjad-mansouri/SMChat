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