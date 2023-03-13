const form = document.getElementById("form-data");
const fileInput = document.getElementById("file");
const tableBody = document.getElementById("table-body");
const nextPageButton = document.getElementById("next-btn");
const prevPageButton = document.getElementById("prev-btn");
const objValDiv = document.getElementById("obj-val");

let currentPage = 0; // Index of the current page
let arrayData = null; // Store the fetched data as an array
let objectData = null; //Store the fetched raw object data (dictionary)

function renderPage(pageIndex) {
  tableBody.innerHTML = "";
  console.log(arrayData);
  let pageData = arrayData[pageIndex];
  console.log(pageData);
  let objVal = pageData[0];
  let lineup = pageData[1];

  console.log("O: ", objVal);

  lineup.forEach((player) => {
    let row = document.createElement("tr");
    let statusCell = document.createElement("td");
    let nameCell = document.createElement("td");
    let projectedPointsCell = document.createElement("td");
    let costCell = document.createElement("td");

    objValDiv.textContent = "Model Objective Value: " + objVal.toString();

    statusCell.textContent = `${player["Status"]}`;
    nameCell.textContent = `${player["Name"]}`;
    projectedPointsCell.textContent = `${player["Projected Points"]}`;
    costCell.textContent = `${player["Cost"]}`;

    row.appendChild(statusCell);
    row.appendChild(nameCell);
    row.appendChild(projectedPointsCell);
    row.appendChild(costCell);

    tableBody.appendChild(row);
  });
}

function handleNextPage() {
  if (currentPage < arrayData.length - 1) {
    if (nextPageButton.disabled) {
      nextPageButton.disabled = false;
    }
    currentPage++;
    console.log("current page:", currentPage);
    renderPage(currentPage);
  } else {
    nextPageButton.disabled = true;
  }
  // enable previous button if currentPage is greater than 0
  if (currentPage > 0) {
    prevPageButton.disabled = false;
  }
}

function handlePrevPage() {
  if (currentPage > 0) {
    if (prevPageButton.disabled) {
      prevPageButton.disabled = false;
    }
    currentPage--;
    console.log("current page:", currentPage);
    renderPage(currentPage);
  } else {
    prevPageButton.disabled = true;
  }
  if (currentPage < arrayData.length - 1) {
    nextPageButton.disabled = false;
  }
}

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
    responseType: "json",
  })
    .then((response) => response.json())
    .then((data) => {
      arrayData = Object.entries(data);
      arrayData.sort(([key1], [key2]) => key2 - key1);
      objectData = Object.fromEntries(arrayData);
      renderPage(currentPage);
    })
    .catch((error) => {
      console.error(error);
      alert("An error occurred while uploading the file.");
    });
});

nextPageButton.addEventListener("click", handleNextPage);
prevPageButton.addEventListener("click", handlePrevPage);
