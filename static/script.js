async function getPrediction() {
    let genres = document.getElementById("genres").value.trim();
    let min_height = document.getElementById("min_height").value;
    let max_height = document.getElementById("max_height").value;
    let min_age = document.getElementById("min_age").value;
    let max_age = document.getElementById("max_age").value;

    let url = `https://actor-prediction.vercel.app/predict?genres=${encodeURIComponent(genres)}&min_height=${min_height}&max_height=${max_height}&min_age=${min_age}&max_age=${max_age}`;

    try {
        let response = await fetch(url);
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        let data = await response.json();
        console.log(data);
        displayResults(data.top_actors);
    } catch (error) {
        document.getElementById("error-message").innerText = "❌ API Error: " + error.message;
    }
}

function displayResults(actors) {
    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = ""; // Clear previous results

    if (!actors || actors.length === 0) {
        resultsDiv.innerHTML = "<p>No matching actors found.</p>";
        return;
    }

    // Create table
    let table = document.createElement("table");
    table.border = "1";
    table.style.margin = "auto";

    // Create table headers
    let headers = ["Actor", "Score", "Genre Match", "Avg Rating", "Previous Movies", "Awards", "Height (m)", "Age"];
    let thead = document.createElement("thead");
    let headerRow = document.createElement("tr");

    headers.forEach(header => {
        let th = document.createElement("th");
        th.textContent = header;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    let tbody = document.createElement("tbody");
    actors.forEach(actor => {
        console.log(actor);
        let row = document.createElement("tr");

        row.innerHTML = `
            <td>${actor.Actor}</td>
            <td>${actor.Actor_Score.toFixed(2)}</td>
            <td>${actor.Genre_Match_Score.toFixed(2)}</td>
            <td>${actor.Avg_Rating.toFixed(1)}</td>
            <td>${actor["Previous Movies"]}</td>
            <td>${actor.Awards}</td>
            <td>${actor.height}</td>
            <td>${actor.Age}</td>
        `;

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    resultsDiv.appendChild(table);
}
