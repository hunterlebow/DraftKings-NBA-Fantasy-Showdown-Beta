const form = document.getElementById("form-data");
const fileInput = document.getElementById("file");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a file to upload.");
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  fetch("/", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text()) // change response.json() to response.text()
    .then((data) => {
      document.getElementById("result").innerHTML = data; // display data in the "result" element
    })
    .catch((error) => {
      console.error(error);
      alert("An error occurred while uploading the file.");
    });
});
