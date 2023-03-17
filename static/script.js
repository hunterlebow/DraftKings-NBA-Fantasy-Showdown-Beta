const form = document.getElementById("form-data");
const fileInput = document.getElementById("file");
const tableBody = document.getElementById("table-body");
const nextPageButton = document.getElementById("next-btn");
const prevPageButton = document.getElementById("prev-btn");
const objValDiv = document.getElementById("obj-val");
const currentPageSpan = document.getElementById("currentPageNumber");
let playerDropdown = document.getElementById("player-dropdown");
const selectedPlayersDiv = document.getElementById("selected-players-div");
const playerSearch = document.getElementById("player-remove-search");
const removePlayerButton = document.getElementById("remove-player-btn");

let currentPage = 0; // Index of the current page
let arrayData = null; // Store the fetched data as an array
let objectData = null; //Store the fetched raw object data (dictionary)
let playerIndex = 1;

function renderPage(pageIndex) {
  playerIndex = 1;
  tableBody.innerHTML = "";
  let pageData = arrayData[pageIndex];
  let objVal = pageData[0];
  let lineup = pageData[1];

  lineup.forEach((player) => {
    let row = document.createElement("tr");

    let indexCell = document.createElement("td");
    let statusCell = document.createElement("td");
    let nameCell = document.createElement("td");
    let projectedPointsCell = document.createElement("td");
    let costCell = document.createElement("td");

    objValDiv.textContent = "Model Objective Value: " + objVal.toString();

    currentPageSpan.textContent =
      (currentPage + 1).toString() + " / " + arrayData.length.toString();

    indexCell.textContent = playerIndex;
    statusCell.textContent = `${player["Status"]}`;
    nameCell.textContent = `${player["Name"]}`;
    projectedPointsCell.textContent = `${player["Projected Points"]}`;
    costCell.textContent = `${player["Cost"]}`;

    row.append(indexCell);
    row.appendChild(statusCell);
    row.appendChild(nameCell);
    row.appendChild(projectedPointsCell);
    row.appendChild(costCell);

    playerIndex++;

    tableBody.appendChild(row);
  });
}

function handleNextPage() {
  if (currentPage < arrayData.length - 1) {
    if (nextPageButton.disabled) {
      nextPageButton.disabled = false;
    }
    currentPage++;
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
      const db = data.db;
      const players = JSON.parse(data.players);
      console.log(players);

      if (playerDropdown.options.length < players.length) {
        populatePlayers(players);
      }

      arrayData = Object.entries(db);
      arrayData.sort(([key1], [key2]) => key2 - key1);

      objectData = Object.fromEntries(arrayData);
      renderPage(currentPage);
      playerSearch.addEventListener("keyup", function () {
        const searchTerm = playerSearch.value.toLowerCase();
        const filteredPlayers = players.filter(function (player) {
          return player.toLowerCase().includes(searchTerm);
        });
        populatePlayers(filteredPlayers);
      });
    })
    .catch((error) => {
      console.error(error);
      alert("An error occurred while uploading the file.");
    });
});

nextPageButton.addEventListener("click", handleNextPage);
prevPageButton.addEventListener("click", handlePrevPage);
removePlayerButton.addEventListener("click", handleSelectedPlayerToRemove);

function populatePlayers(playersList) {
  playerDropdown.innerHTML = "";
  console.log(playersList);
  playersList.forEach((player) => {
    const option = document.createElement("option");
    option.value = player;
    option.text = player;
    playerDropdown.add(option);
  });
}

function handleSelectedPlayerToRemove() {
  const selectedPlayers = Array.from(playerDropdown.selectedOptions).map(
    (option) => option.value
  );
  console.log(selectedPlayers); // REMOVE FROM DATASET
}

playerDropdown.addEventListener("change", () => {
  const selectedPlayerCard = document.createElement("div");
  selectedPlayerCard.classList.add("selected-player-card");
  selectedPlayerCard.textContent = playerDropdown.value;
  const removeCardButton = document.createElement("button");
  removeCardButton.classList.add("remove-card-button");
  removeCardButton.textContent = "x";
  selectedPlayerCard.appendChild(removeCardButton);
  selectedPlayersDiv.appendChild(selectedPlayerCard);
  playerSearch.value = "";
  playerDropdown.selectedIndex = -1;
});

selectedPlayersDiv.addEventListener("click", (event) => {
  if (event.target.classList.contains("remove-card-button")) {
    event.target.parentElement.remove();
  }
});
