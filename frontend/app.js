// DOM elements
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const fileUpload = document.getElementById("file-upload");
const uploadStatus = document.getElementById("upload-status");
const chunkCount = document.getElementById("chunk-count");
const clearBtn = document.getElementById("clear-btn");

const API_BASE = "/api";

// ---- Chat ----

let isStreaming = false;

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = chatInput.value.trim();
    if (!question || isStreaming) return;

    // Remove welcome message
    const welcome = chatMessages.querySelector(".welcome-message");
    if (welcome) welcome.remove();

    addMessage("user", question);
    chatInput.value = "";
    autoResizeTextarea();

    await streamResponse(question);
});

// Auto-resize textarea
chatInput.addEventListener("input", autoResizeTextarea);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit"));
    }
});

function autoResizeTextarea() {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + "px";
}

function addMessage(role, text) {
    const avatar = role === "user" ? "U" : "AI";
    const label = role === "user" ? "You" : "Assistant";

    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-role">${label}</div>
            <div class="message-text">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
}

function createStreamingMessage() {
    const div = document.createElement("div");
    div.className = "message assistant";
    div.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
            <div class="message-role">Assistant</div>
            <div class="message-text"><span class="cursor"></span></div>
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
    return div.querySelector(".message-text");
}

async function streamResponse(question) {
    isStreaming = true;
    sendBtn.disabled = true;

    const textEl = createStreamingMessage();
    let fullText = "";

    try {
        const response = await fetch(`${API_BASE}/chat/stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (!line.startsWith("data: ")) continue;
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue;

                try {
                    const data = JSON.parse(jsonStr);

                    if (data.error) {
                        fullText += `\n\n[Error: ${data.error}]`;
                        textEl.textContent = fullText;
                        break;
                    }

                    if (data.done) break;

                    if (data.token) {
                        fullText += data.token;
                        // Remove cursor, set text, re-add cursor
                        textEl.innerHTML =
                            escapeHtml(fullText) +
                            '<span class="cursor"></span>';
                        scrollToBottom();
                    }
                } catch {
                    // Skip malformed JSON
                }
            }
        }
    } catch (err) {
        fullText = fullText || "";
        fullText += `\n\n[Connection error: ${err.message}. Make sure Ollama is running.]`;
    }

    // Remove cursor when done
    textEl.textContent = fullText;
    isStreaming = false;
    sendBtn.disabled = false;
    chatInput.focus();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Suggestion buttons
function askSuggestion(el) {
    chatInput.value = el.textContent;
    chatForm.dispatchEvent(new Event("submit"));
}

// ---- File Upload ----

fileUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    uploadStatus.textContent = `Uploading ${file.name}...`;
    uploadStatus.className = "upload-status loading";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Upload failed");
        }

        const data = await response.json();
        uploadStatus.textContent = `${data.filename}: ${data.chunks} chunks ingested`;
        uploadStatus.className = "upload-status success";
        refreshStatus();
    } catch (err) {
        uploadStatus.textContent = `Error: ${err.message}`;
        uploadStatus.className = "upload-status error";
    }

    fileUpload.value = "";
});

// ---- Store Management ----

clearBtn.addEventListener("click", async () => {
    if (!confirm("Delete all documents from the knowledge base?")) return;

    try {
        await fetch(`${API_BASE}/documents`, { method: "DELETE" });
        uploadStatus.textContent = "All documents cleared.";
        uploadStatus.className = "upload-status success";
        refreshStatus();
    } catch (err) {
        uploadStatus.textContent = `Error: ${err.message}`;
        uploadStatus.className = "upload-status error";
    }
});

async function refreshStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        chunkCount.textContent = `${data.document_chunks} chunks stored`;
    } catch {
        chunkCount.textContent = "Unable to connect to server";
    }
}

// Initial status check
refreshStatus();
