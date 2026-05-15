const auth = new Auth()
let toastContainer = null;

function getToastContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }
  return toastContainer;
}


function showToast(message, type = 'success', duration = 3500) {
  const container = getToastContainer();
  const toast = document.createElement('div');
  toast.className = 'toast-message';

  // Determine icon and additional styling
  let icon = '✓';
  if (type === 'error') {
    toast.classList.add('toast-error');
    icon = '⚠️';
  } else if (type === 'warning') {
    toast.classList.add('toast-warning');
    icon = '⚡';
  } else if (type === 'info') {
    toast.classList.add('toast-info');
    icon = 'ℹ️';
  } else {
    icon = '✓';
  }

  // Handle multiple error messages (array)
  if (Array.isArray(message) && message.length > 1 && type === 'error') {
    toast.classList.add('error-list');
    const errorListHtml = document.createElement('div');
    errorListHtml.style.width = '100%';
    errorListHtml.innerHTML = `
        <strong>${icon} ${message.length} issue(s) found:</strong>
        <ul>
          ${message.map(err => `<li>• ${escapeHtml(err)}</li>`).join('')}
        </ul>
      `;
    toast.appendChild(errorListHtml);
  } else if (Array.isArray(message) && message.length === 1) {
    // Single error from array
    toast.innerHTML = `<span class="toast-icon">${icon}</span> <span>${escapeHtml(message[0])}</span>`;
  } else if (typeof message === 'string') {
    toast.innerHTML = `<span class="toast-icon">${icon}</span> <span>${escapeHtml(message)}</span>`;
  } else {
    toast.innerHTML = `<span class="toast-icon">${icon}</span> <span>Operation completed</span>`;
  }

  container.appendChild(toast);

  // Auto-remove after duration
  const timeoutId = setTimeout(() => {
    removeToast(toast);
  }, duration);

  // Store timeout for cleanup if needed
  toast.dataset.timeoutId = timeoutId;

  // Hover pause: clear timeout on mouseenter, restore on mouseleave
  toast.addEventListener('mouseenter', () => {
    if (toast.dataset.timeoutId) {
      clearTimeout(parseInt(toast.dataset.timeoutId));
      toast.dataset.timeoutId = null;
    }
  });

  toast.addEventListener('mouseleave', () => {
    if (!toast.dataset.timeoutId) {
      const newTimeout = setTimeout(() => removeToast(toast), 2000);
      toast.dataset.timeoutId = newTimeout;
    }
  });

  return toast;
}

function removeToast(toastElement) {
  if (toastElement.dataset.timeoutId) {
    clearTimeout(parseInt(toastElement.dataset.timeoutId));
  }
  toastElement.classList.add('removing');
  setTimeout(() => {
    if (toastElement.parentNode) toastElement.parentNode.removeChild(toastElement);
  }, 200);
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
const saveBtn = document.getElementById("saveAllBtn");
saveBtn.addEventListener("click", () => {
  const newFirstName = document.getElementById("firstNameInput").value.trim();
  const newLastName = document.getElementById("lastNameInput").value.trim();
  const newUsername = document.getElementById("usernameInput").value.trim();
  const newEmail = document.getElementById("emailInput").value.trim();
  const newBirthday = document.getElementById("birthdayInput").value;
  const newBio = document.getElementById("bioInput").value.trim();
  const newProfileImage = document.getElementById("avatarUpload").files[0];


  const formData = new FormData()
  formData.append("user.username", newUsername)
  formData.append("user.email", newEmail)
  formData.append("user.first_name", newFirstName)
  formData.append("user.last_name", newLastName)
  formData.append("birth_day", newBirthday)
  formData.append("bio", newBio)
  if (newProfileImage != undefined) {

    formData.append("profile_image", newProfileImage)
  }



  changeAccount(formData)
})

async function changeAccount(formData) {
  const origin = window.location.origin
  const response = await auth.authenticatedRequest(`${origin}/api/update-account/`, formData, "PATCH", {}, "multipart/form-data")
  const data = await response.json()



  if (response.ok) {
    showToast("Changes saved")
  } else {

    Object.entries(data).forEach(([key, values]) => {
      if (Array.isArray(values)) {
        values.forEach(error => {
          showToast(`${key}: ${error}`, "error")

        })
      } else if (typeof values === "object" && values !== null) {

        Object.entries(values).forEach(([key, values]) => {
          showToast(`${key}: ${values}`, "error")

        })
      }
    })

  }
}

document.getElementById("changePhotoBtn").addEventListener("click", () => {
  document.getElementById("avatarUpload").click();

});

document.getElementById("avatarUpload").addEventListener("change", function() {
  const file = this.files[0]
  const reader = new FileReader();

  const accountAvatarImg = document.getElementById("accountAvatarImg")
  reader.onload = function(e) {
    accountAvatarImg.src = e.target.result;
  }
  reader.readAsDataURL(file)
})



const modal = document.getElementById("deleteModal");
const modalConfirmInput = document.getElementById("modalConfirmInput");
const modalConfirmBtn = document.getElementById("modalConfirmDeleteBtn");
const modalCancelBtn = document.getElementById("modalCancelBtn");
const deleteTriggerBtn = document.getElementById("deleteAccountBtn");

function openDeleteModal() {
  modal.classList.add("active");
  modalConfirmInput.value = "";
  modalConfirmBtn.disabled = true;
  modalConfirmInput.focus();
}

function closeDeleteModal() {
  modal.classList.remove("active");
}

function handleDeleteConfirmation() {
  const typedValue = modalConfirmInput.value.trim();
  if (typedValue === "DELETE") {
    // Permanent deletion

    closeDeleteModal();
    showToast("Account permanently deleted. Redirecting...", "info", 2000);
    setTimeout(() => {
      document.getElementById("delete-form").submit()
    }, 1600);
  } else {
    showToast("Deletion cancelled — confirmation keyword does not match", "error", 3500);
    closeDeleteModal();
  }
}

// Enable/disable confirm button based on input
modalConfirmInput.addEventListener("input", (e) => {
  const isValid = e.target.value.trim() === "DELETE";
  modalConfirmBtn.disabled = !isValid;
});

deleteTriggerBtn.addEventListener("click", openDeleteModal);
modalCancelBtn.addEventListener("click", closeDeleteModal);
modalConfirmBtn.addEventListener("click", handleDeleteConfirmation);

// Close modal on overlay click (but not on container)
modal.addEventListener("click", (e) => {
  if (e.target === modal) closeDeleteModal();
});

document.addEventListener("keydown", (e) => {
  if (modal.classList.contains("active") && e.key === "Escape") closeDeleteModal();
  if (modal.classList.contains("active") && e.key === "Enter" && !modalConfirmBtn.disabled) handleDeleteConfirmation();
});