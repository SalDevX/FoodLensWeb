document.addEventListener("DOMContentLoaded", function () {
    // Define the searchItem function
    function searchItem() {
        const itemName = document.getElementById("itemInput").value; // Get item name from the input
        const fileInput = document.getElementById("fileInput"); // Get file input

        if (!itemName || !fileInput.files[0]) {
            alert("Please enter an item name and select a file.");
            return;
        }

        const formData = new FormData();
        formData.append('item_name', itemName);
        formData.append('file', fileInput.files[0]);

        // Sending the request to the Flask server
        fetch('http://127.0.0.1:5000/search', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Process and display search results
            const tableBody = document.querySelector("#resultsTable tbody");
            tableBody.innerHTML = '';  // Clear previous results

            if (data.error) {
                alert(data.error);
            } else if (data.length === 0) {
                alert('No items found.');
            } else {
                // Populate the table with results
                data.forEach(result => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${result.sheet}</td>
                        <td>${result.summary}</td>
                        <td>${result.price}</td>
                    `;
                    tableBody.appendChild(row);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an error with the search request. Please check the console for more details.');
        });
    }

    // Attach the searchItem function to the button
    const searchButton = document.querySelector("button");
    searchButton.addEventListener("click", searchItem);
});

