document.addEventListener("DOMContentLoaded", function () {
    // Define the searchItem function
    function searchItem() {
        const itemName = document.getElementById("itemInput").value.trim(); // Trim to avoid blank spaces
        const fileInput = document.getElementById("fileInput");

        if (!itemName || !fileInput.files[0]) {
            alert("Please enter an item name and select a file.");
            return;
        }

        const formData = new FormData();
        formData.append('item_name', itemName);
        formData.append('file', fileInput.files[0]);

        // Use a relative path to work on both local and Fly.io
        fetch('/search', {
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
            const tableBody = document.querySelector("#resultsTable tbody");
            tableBody.innerHTML = '';  // Clear previous results

            if (data.error) {
                alert(data.error);
            } else if (data.length === 0) {
                alert('No items found.');
            } else {
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
            console.error('Search request failed:', error);
            alert('There was an error with the search request. Please check your internet connection or try again later.');
        });
    }

    // Attach the searchItem function to the button
    const searchButton = document.getElementById("searchButton");
    if (searchButton) {
        searchButton.addEventListener("click", searchItem);
    } else {
        console.error("Search button not found.");
    }
});

