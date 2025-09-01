class SentientChat {
  constructor() {
    this.apiBase = "http://localhost:8000";
    this.init();
  }

  init() {
    this.bindEvents();
    this.loadTemplates();
  }

  bindEvents() {
    // Send button click
    document.getElementById("sendButton").addEventListener("click", () => {
      this.sendMessage();
    });

    // Enter key in input
    document.getElementById("promptInput").addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.sendMessage();
      }
    });

    // Template buttons
    document.querySelectorAll(".template-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const template = e.target.dataset.template;
        this.applyTemplate(template);
      });
    });
  }

  applyTemplate(template) {
    const input = document.getElementById("promptInput");
    if (input.value.trim() === "") {
      input.value = `${template} `;
    } else {
      input.value = `${template} ${input.value}`;
    }
    input.focus();
  }

  async sendMessage() {
    const input = document.getElementById("promptInput");
    const prompt = input.value.trim();

    if (!prompt) return;

    // Add user message to chat
    this.addMessage("user", prompt);
    input.value = "";

    try {
      // Show loading state
      const loadingMessage = this.addMessage("ai", "Thinking...", true);

      // Call API
      const response = await fetch(
        `${this.apiBase}/api/stream?prompt=${encodeURIComponent(prompt)}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Process streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = "";
      let isImageResponse = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              // Check if this is an image response
              if (this.processChunkData(data)) {
                isImageResponse = true;
                loadingMessage.remove();
                continue;
              }

              if (data.type === "AI_RESPONSE_CHUNK") {
                aiResponse += data.data;
                this.updateLastMessage(aiResponse);
              }
            } catch (e) {
              console.log("Raw chunk:", line);
            }
          }
        }
      }

      // If it was a text response and we have content, remove loading
      if (!isImageResponse && aiResponse) {
        const tempMessages = document.querySelectorAll(".temp-message");
        tempMessages.forEach((msg) => msg.remove());
      }
    } catch (error) {
      console.error("Error:", error);
      this.updateLastMessage(
        "Sorry, I encountered an error. Please try again."
      );
    }
  }

  processChunkData(data) {
    if (data.type === "IMAGE_GENERATED") {
      this.displayImage(data.data);
      return true;
    }
    return false;
  }

  displayImage(imageData) {
    const messagesContainer = document.getElementById("chatMessages");

    const messageDiv = document.createElement("div");
    messageDiv.className = "message ai-message";
    messageDiv.innerHTML = `
            <div class="message-avatar">🎨</div>
            <div class="message-content">
                <p><strong>Image Generated Successfully!</strong></p>
                <div class="generated-image">
                    <img src="${imageData.image_url}" alt="${imageData.prompt}" 
                         style="max-width: 100%; border-radius: 10px; margin-top: 10px;">
                    <div class="image-info">
                        <p class="image-prompt"><strong>Prompt:</strong> ${this.escapeHtml(
                          imageData.prompt
                        )}</p>
                    </div>
                </div>
            </div>
        `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  addMessage(role, content, isTemp = false) {
    const messagesContainer = document.getElementById("chatMessages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}-message ${
      isTemp ? "temp-message" : ""
    }`;
    messageDiv.innerHTML = `
            <div class="message-avatar">${role === "ai" ? "🤖" : "👤"}</div>
            <div class="message-content">
                <p>${this.escapeHtml(content)}</p>
            </div>
        `;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return messageDiv;
  }

  updateLastMessage(content) {
    const messages = document.getElementById("chatMessages");
    const lastMessage = messages.lastChild;
    if (lastMessage && lastMessage.classList.contains("temp-message")) {
      lastMessage.querySelector(".message-content p").innerHTML =
        this.escapeHtml(content);
      messages.scrollTop = messages.scrollHeight;
    }
  }

  async loadTemplates() {
    try {
      const response = await fetch(`${this.apiBase}/api/templates`);
      if (response.ok) {
        const data = await response.json();
        this.updateTemplatesUI(data.templates);
      }
    } catch (error) {
      console.error("Error loading templates:", error);
    }
  }

  updateTemplatesUI(templates) {
    const templatesGrid = document.querySelector(".templates-grid");
    if (templatesGrid && templates) {
      templatesGrid.innerHTML = Object.entries(templates)
        .map(
          ([name, desc]) => `
                    <div class="template-card">
                        <h4>${name}</h4>
                        <p>${desc}</p>
                    </div>
                `
        )
        .join("");
    }
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize chat when page loads
document.addEventListener("DOMContentLoaded", () => {
  new SentientChat();
});
