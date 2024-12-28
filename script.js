document.getElementById("travelForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const source = document.getElementById("source").value;
    const destination = document.getElementById("destination").value;
    const days = document.getElementById("days").value;

    const payload = {
        query: "Create a travel plan for me",
        days: parseInt(days, 10),
        source_name: source,
        destination_name: destination
    };

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error("Failed to fetch travel plan");
        }

        const data = await response.json();
        displayOutput(data.message);
    } catch (error) {
        document.getElementById("output").textContent = `Error: ${error.message}`;
    }
});

function displayOutput(plan) {
    const outputDiv = document.getElementById("output");
    outputDiv.innerHTML = `
        <h2>Travel Plan</h2>
        <p><strong>Days:</strong> ${plan.days}</p>
        <p><strong>Source:</strong> ${plan.source}</p>
        <p><strong>Destination:</strong> ${plan.destination}</p>
        <p><strong>Route Summary:</strong> ${plan.route_summary}</p>
        <h3>Steps:</h3>
        <ul>
            ${plan.steps.map(step => `<li>${step}</li>`).join("")}
        </ul>
        <h3>Places to Visit:</h3>
        <ul>
            ${plan.places_to_visit.map(place => `<li><strong>${place.name}</strong> - ${place.address} (Rating: ${place.rating})</li>`).join("")}
        </ul>
    `;
}