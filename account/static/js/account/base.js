async function fetchPOST(url, formData) {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken
    },
    body: formData
  })
  const data = await response.json()
  return data
}