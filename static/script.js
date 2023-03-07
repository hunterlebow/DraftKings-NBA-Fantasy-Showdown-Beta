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
    .then((response) => response.json())
    .then((data) => {
      data = data.data;
      const tableBody = document.getElementById("table-body");
      tableBody.innerHTML = "";
      data.forEach((item) => {
        const row = document.createElement("tr");
        const statusCell = document.createElement("td");
        const nameCell = document.createElement("td");
        const projectedPointsCell = document.createElement("td");
        const costCell = document.createElement("td");

        statusCell.textContent = item.Status;
        nameCell.textContent = item.Name;
        projectedPointsCell.textContent = item["Projected Points"];
        costCell.textContent = item.Cost;
        row.appendChild(statusCell);
        row.appendChild(nameCell);
        row.appendChild(projectedPointsCell);
        row.appendChild(costCell);

        tableBody.appendChild(row);
      });
    })
    .catch((error) => {
      console.error(error);
      alert("An error occurred while uploading the file.");
    });
});