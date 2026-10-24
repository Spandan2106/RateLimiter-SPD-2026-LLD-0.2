
const API_URL = "http://127.0.0.1:8000/limited";

const algorithmInput = document.getElementById("algorithm");
const clientInput = document.getElementById("clientId");
const countInput = document.getElementById("requestCount");
const sendButton = document.getElementById("sendBtn");
const clearButton = document.getElementById("clearBtn");

const allowedElement = document.getElementById("allowed");
const rejectedElement = document.getElementById("rejected");
const totalElement = document.getElementById("total");
const resultsElement = document.getElementById("results");
const messageElement = document.getElementById("message");

let allowed = 0;
let rejected = 0;
let total = 0;

function updateStats() {
    allowedElement.textContent = allowed;
    rejectedElement.textContent = rejected;
    totalElement.textContent = total;
}

function showResult(text, type) {
    const item = document.createElement("div");
    item.className = `result ${type}`;
    item.textContent = text;
    resultsElement.prepend(item);
}

async function sendOneRequest(algorithm, clientId, requestNumber) {
    const params = new URLSearchParams({
        algorithm,
        client_id: clientId
    });

    try {
        const response = await fetch(`${API_URL}?${params}`);

        const body = await response.json().catch(() => ({}));

        total++;

        if (response.ok) {
            allowed++;
            showResult(
                `Request ${requestNumber}: ALLOWED`,
                "success"
            );
        } else if (response.status === 429) {
            rejected++;
            showResult(
                `Request ${requestNumber}: REJECTED (429)`,
                "failure"
            );
        } else {
            showResult(
                `Request ${requestNumber}: HTTP ${response.status}`,
                "error"
            );
        }

        updateStats();
        return body;
    } catch (error) {
        showResult(
            `Request ${requestNumber}: Could not reach backend`,
            "error"
        );
        return null;
    }
}

sendButton.addEventListener("click", async () => {
    const algorithm = algorithmInput.value;
    const clientId = clientInput.value.trim();
    const count = Number(countInput.value);

    if (!clientId || !Number.isInteger(count) ||
        count < 1 || count > 100) {
        messageElement.textContent =
            "Enter a client ID and a request count from 1 to 100.";
        return;
    }

    sendButton.disabled = true;
    messageElement.textContent =
        `Sending ${count} requests using ${algorithm}...`;

    try {
        // Sequential requests make the order easier to observe.
        for (let i = 1; i <= count; i++) {
            await sendOneRequest(algorithm, clientId, i);
        }

        messageElement.textContent = "Request batch completed.";
    } finally {
        sendButton.disabled = false;
    }
});

clearButton.addEventListener("click", () => {
    allowed = 0;
    rejected = 0;
    total = 0;

    resultsElement.replaceChildren();
    messageElement.textContent = "Results cleared.";
    updateStats();
});

updateStats();
