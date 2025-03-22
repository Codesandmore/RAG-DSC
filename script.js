const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");
const attachBtn = document.getElementById("attach-btn");
const fileInput = document.getElementById("file-input");
const pdfPreview = document.getElementById("pdf-preview");

let uploadedFile = null;

attachBtn.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];

    if (file && file.type === "application/pdf") {
        uploadedFile = file;

        pdfPreview.innerHTML = `
            <div class="pdf-preview-card">
                <div class="pdf-icon-container">
                    <span class="pdf-icon">📄</span>
                </div>
                <div class="pdf-info">
                    <span class="pdf-name">${uploadedFile.name}</span>
                    <span class="pdf-subtext">PDF</span>
                </div>
                <button class="remove-pdf" onclick="removePDF()">❌</button>
            </div>
        `;
        pdfPreview.style.display = "flex";
    }
});

function removePDF() {
    uploadedFile = null;
    pdfPreview.innerHTML = "";
    pdfPreview.style.display = "none";
    fileInput.value = "";
}

userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);

function sendMessage() {
    let messageText = userInput.value.trim();
    if (!messageText && !uploadedFile) return;

    let messageContainer = document.createElement("div");
    messageContainer.classList.add("message-container", "user");

    if (uploadedFile) {
        let pdfBubble = document.createElement("div");
        pdfBubble.classList.add("message", "pdf-bubble");

        let fileNameContainer = document.createElement("div");
        fileNameContainer.classList.add("pdf-bubble-card");

        let iconContainer = document.createElement("div");
        iconContainer.classList.add("pdf-icon-container");
        iconContainer.innerHTML = `<span class="pdf-icon">📄</span>`;

        let textContainer = document.createElement("div");
        textContainer.classList.add("pdf-info");
        textContainer.innerHTML = `
            <span class="pdf-name">${uploadedFile.name}</span>
            <span class="pdf-subtext">PDF</span>
        `;

        fileNameContainer.appendChild(iconContainer);
        fileNameContainer.appendChild(textContainer);
        pdfBubble.appendChild(fileNameContainer);
        messageContainer.appendChild(pdfBubble);
        removePDF();
    }

    if (messageText) {
        let userMessage = document.createElement("div");
        userMessage.classList.add("message");
        userMessage.innerHTML = messageText.replace(/\n/g, "<br>");
        messageContainer.appendChild(userMessage);
    }

    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    setTimeout(() => {
        generateBotResponse(messageText);
    }, 500);

    userInput.value = "";
    userInput.style.height = "20px"; 
}

function generateBotResponse(userMessage) {
    let botResponseText = getBotResponse(userMessage);

    let botMessageContainer = document.createElement("div");
    botMessageContainer.classList.add("message-container", "bot");

    let botMessage = document.createElement("div");
    botMessage.classList.add("message", "bot-message");
    botMessage.innerHTML = botResponseText;

    botMessageContainer.appendChild(botMessage);
    chatBox.appendChild(botMessageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function getBotResponse(userMessage) {
    userMessage = userMessage.toLowerCase();

    if (userMessage.includes("hello") || userMessage.includes("hi")) {
        return "Hello! How can I assist you today? 😊";
    } else if (userMessage.includes("how are you")) {
        return "I'm just a bot, but I'm here to help! What do you need? 🤖";
    } else if (userMessage.includes("pdf")) {
        return "You uploaded a PDF! Let me know if you need any help with it. 📄";
    } else if (userMessage.includes("bye")) {
        return "Goodbye! Have a great day! 👋";
    } else {
        return "I'm not sure how to respond to that, but I'm here to help! 😊";
    }
}
