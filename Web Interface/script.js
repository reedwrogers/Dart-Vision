document.addEventListener("DOMContentLoaded", () => {
    const imageUpload = document.getElementById("imageUpload")
    const imageContainer = document.getElementById("imageContainer")
  
    imageUpload.addEventListener("change", (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const img = document.createElement("img")
          img.src = e.target.result
          img.alt = "Uploaded game image"
          imageContainer.innerHTML = ""
          imageContainer.appendChild(img)
        }
        reader.readAsDataURL(file)
      }
    })
  })
  