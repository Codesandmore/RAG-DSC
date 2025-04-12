document.addEventListener("DOMContentLoaded", function() {
    // Get all elements
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const sendBtn = document.getElementById("send-btn");
    const attachBtn = document.getElementById("attach-btn");
    const fileInput = document.getElementById("file-input");
    const pdfPreview = document.getElementById("pdf-preview");
    
    let uploadedFile = null;
    
    // Prevent any unintentional form submissions throughout the document
    document.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log("Form submission prevented");
        return false;
    });
    
    // File attachment flow
    if (attachBtn) {
        attachBtn.addEventListener("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("Attach button clicked");
            fileInput.click();
            return false;
        });
    }
    
    // Handle file selection
    if (fileInput) {
        fileInput.addEventListener("change", function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("File selected");
            
            const file = this.files[0];
            if (!file || file.type !== "application/pdf") {
                console.log("Not a PDF or no file selected");
                return false;
            }
            
            console.log("Processing PDF:", file.name);
            uploadedFile = file;
            
            // Show file in preview area
            pdfPreview.style.display = "flex";
            pdfPreview.innerHTML = `
                <div class="pdf-preview-card">
                    <div class="pdf-icon">📄</div>
                    <div class="pdf-info">
                        <span class="pdf-name">${file.name}</span>
                        <span class="pdf-size">${(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                    <button type="button" class="remove-pdf-btn">×</button>
                </div>
            `;
            
            // Add event listener to remove button
            const removeBtn = document.querySelector(".remove-pdf-btn");
            if (removeBtn) {
                removeBtn.addEventListener("click", function(evt) {
                    evt.preventDefault();
                    evt.stopPropagation();
                    removePDF();
                    return false;
                });
            }
            
            // Show file in chat
            const messageContainer = document.createElement("div");
            messageContainer.classList.add("message-container", "user");
            
            const pdfBubble = document.createElement("div");
            pdfBubble.classList.add("message", "pdf-bubble");
            
            const fileNameContainer = document.createElement("div");
            fileNameContainer.classList.add("pdf-bubble-card");
            
            const iconContainer = document.createElement("div");
            iconContainer.classList.add("pdf-icon-container");
            iconContainer.innerHTML = `<span class="pdf-icon">📄</span>`;
            
            const textContainer = document.createElement("div");
            textContainer.classList.add("pdf-info");
            textContainer.innerHTML = `
                <span class="pdf-name">${file.name}</span>
                <span class="pdf-subtext">PDF</span>
            `;
            
            fileNameContainer.appendChild(iconContainer);
            fileNameContainer.appendChild(textContainer);
            pdfBubble.appendChild(fileNameContainer);
            messageContainer.appendChild(pdfBubble);
            chatBox.appendChild(messageContainer);
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Upload without page reload
            uploadFileAsync(file);
            
            return false;
        });
    }
    
    // Async file upload to prevent page reload
    async function uploadFileAsync(file) {
        console.log("Starting async file upload");
        
        // Create processing message
        const processingContainer = document.createElement("div");
        processingContainer.classList.add("message-container", "bot");
        
        const processingMessage = document.createElement("div");
        processingMessage.classList.add("message", "bot-message");
        processingMessage.innerHTML = `
            <div class="processing-text">Processing PDF "${file.name}"...</div>
            <div class="typing-indicator"><span></span><span></span><span></span></div>
        `;
        
        processingContainer.appendChild(processingMessage);
        chatBox.appendChild(processingContainer);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Start timing
        const startTime = performance.now();
        
        try {
            // Create form data
            const formData = new FormData();
            formData.append("file", file);
            
            console.log("Sending fetch request for PDF upload");
            
            // Use fetch with no-redirect mode
            const response = await fetch("http://127.0.0.1:8000/upload-pdf", {
                method: "POST",
                body: formData,
                redirect: 'follow',
                mode: 'cors',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            
            // Parse response JSON
            const data = await response.json();
            console.log("Upload response:", data);
            
            // Calculate timing
            const endTime = performance.now();
            const processingTime = ((endTime - startTime) / 1000).toFixed(2);
            
            // Update processing message
            processingMessage.innerHTML = `
                <div class="success-message">
                    ✅ PDF "${file.name}" processed successfully!<br>
                    Processing time: ${processingTime}s<br>
                    ${data.chunks ? `${data.chunks} chunks added to knowledge base` : ''}
                </div>
            `;
            
        } catch (error) {
            console.error("Upload error:", error);
            processingMessage.innerHTML = `
                <div class="error-message">
                    ❌ Error processing PDF "${file.name}"<br>
                    ${error.message}
                </div>
            `;
        } finally {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }
    
    // Clean PDF removal
    function removePDF() {
        uploadedFile = null;
        pdfPreview.innerHTML = "";
        pdfPreview.style.display = "none";
        fileInput.value = "";
    }
    
    // Message sending with async handling
    if (sendBtn) {
        sendBtn.addEventListener("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            sendMessage();
            return false;
        });
    }
    
    // Enter key handling for messages
    if (userInput) {
        userInput.addEventListener("keydown", function(e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.stopPropagation();
                sendMessage();
                return false;
            }
        });
    }
    
    // Main message sending function
    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (!messageText && !uploadedFile) return;
        
        console.log("Sending message:", messageText);
        
        // Process user message
        if (messageText) {
            // Create user message element
            const messageContainer = document.createElement("div");
            messageContainer.classList.add("message-container", "user");
            
            const userMessageElement = document.createElement("div");
            userMessageElement.classList.add("message");
            userMessageElement.innerHTML = messageText.replace(/\n/g, "<br>");
            
            messageContainer.appendChild(userMessageElement);
            chatBox.appendChild(messageContainer);
            
            // Clear input IMMEDIATELY
            userInput.value = "";
            
            // Show typing indicator
            const typingContainer = document.createElement("div");
            typingContainer.classList.add("message-container", "bot", "typing-indicator-container");
            typingContainer.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
            chatBox.appendChild(typingContainer);
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Send to API
            try {
                const startTime = performance.now();
                
                const response = await fetch("http://127.0.0.1:8000/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ message: messageText }),
                    redirect: 'follow'
                });
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                const data = await response.json();
                const endTime = performance.now();
                const responseTime = ((endTime - startTime) / 1000).toFixed(2);
                
                // Remove typing indicator
                chatBox.removeChild(typingContainer);
                
                // Show response
                const botContainer = document.createElement("div");
                botContainer.classList.add("message-container", "bot");
                
                const botMessage = document.createElement("div");
                botMessage.classList.add("message", "bot-message");
                botMessage.innerHTML = data.response.replace(/\n/g, "<br>");
                
                const timeInfo = document.createElement("div");
                timeInfo.classList.add("response-time");
                timeInfo.textContent = `Response time: ${responseTime}s`;
                
                botContainer.appendChild(botMessage);
                botContainer.appendChild(timeInfo);
                chatBox.appendChild(botContainer);
                
            } catch (error) {
                console.error("Error sending message:", error);
                
                // Remove typing indicator
                chatBox.removeChild(typingContainer);
                
                // Show error message
                const errorContainer = document.createElement("div");
                errorContainer.classList.add("message-container", "bot");
                
                const errorMessage = document.createElement("div");
                errorMessage.classList.add("message", "bot-message", "error");
                errorMessage.textContent = "Error: Could not connect to server. Please try again later.";
                
                errorContainer.appendChild(errorMessage);
                chatBox.appendChild(errorContainer);
            } finally {
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }
    }
});
