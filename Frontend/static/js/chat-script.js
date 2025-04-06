/**
 * Trade'n Offer Chat System
 * Handles all chat-related functionality, including:
 * - Loading and displaying chat rooms
 * - Sending and receiving messages with image support
 * - Displaying trade details
 */

// ==================== Global State ====================
let currentOfferId = null; // Currently active chat offer ID
let currentChatPartner = null; // Current chat partner username
let currentUserId = null; // Current user ID
let chatRooms = []; // List of all chat rooms
let loadedMessages = {}; // Cache for loaded messages
let messageTimestamps = {}; // Timestamp tracking for messages
let currentImageData = null; // Current selected image data (base64)
let isMessageSending = false; // Flag to prevent double-sending

// ==================== Initialization ====================
/**
 * Initialize the chat system
 */
async function initializeChat() {
  console.log("Starting chat system initialization...");

  try {
    // Initialize user
    await initializeUser();

    // Setup event handlers
    setupEventHandlers();

    // Initial load of chat list
    await updateChatList();

    // Start polling for updates
    startPolling();

    console.log("Chat initialization complete");
  } catch (error) {
    console.error(`Chat initialization error: ${error.message}`);
  }
}

/**
 * Load and display chat messages
 */
async function loadChatMessages(offerId, forceUpdate = false) {
  try {
    // Get messages container
    const messagesContainer = document.getElementById("chatMessages");
    if (!messagesContainer) return;

    // Always get fresh messages when switching chats or when forced
    if (forceUpdate || !loadedMessages[offerId]) {
      // Show loading
      messagesContainer.innerHTML = `
                <div class="loading-messages">
                    <i class="fas fa-spinner fa-spin"></i> Loading messages...
                </div>
            `;

      // Fetch messages for this chat
      const messages = await fetchMessages(offerId);

      // Store messages and timestamp
      loadedMessages[offerId] = messages;
      if (messages.length > 0) {
        messageTimestamps[offerId] = Math.max(
          ...messages.map((m) => m.timestamp || 0)
        );
      } else {
        messageTimestamps[offerId] = 0;
      }

      // Display messages
      displayMessages(messages, messagesContainer);
    } else {
      // If we already have messages, just check for new ones
      const latestTimestamp = messageTimestamps[offerId] || 0;
      const newMessages = await fetchNewMessages(offerId, latestTimestamp);

      if (newMessages.length > 0) {
        // Add new messages
        appendNewMessages(newMessages, messagesContainer);

        // Update cached messages
        loadedMessages[offerId] = [...loadedMessages[offerId], ...newMessages];
        messageTimestamps[offerId] = Math.max(
          ...newMessages.map((m) => m.timestamp || 0)
        );
      }
    }

    // Mark messages as read
    fetch(`/chat/mark-as-read/${offerId}`, {
      method: "POST",
      credentials: "include",
    }).catch((err) => console.warn("Error marking messages as read:", err));
  } catch (error) {
    console.error(`Error loading messages: ${error.message}`);

    // Show error message
    const messagesContainer = document.getElementById("chatMessages");
    if (messagesContainer) {
      messagesContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error loading messages</p>
                    <small>Please try again</small>
                </div>
            `;
    }
  }
}

/**
 * Display messages in container
 */
function displayMessages(messages, container) {
  // Clear current messages
  container.innerHTML = "";

  if (!messages || messages.length === 0) {
    // Show empty state
    container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-comment-alt"></i>
                <p>No messages yet</p>
                <small>Start the conversation!</small>
            </div>
        `;
    return;
  }

  // Group messages by date
  let currentDate = "";

  for (const message of messages) {
    // Check if we need to add a date separator
    if (message.timestamp) {
      const messageDate = new Date(message.timestamp);
      if (!isNaN(messageDate.getTime())) {
        const formattedDate = formatDate(messageDate);

        if (formattedDate !== currentDate) {
          currentDate = formattedDate;

          // Add date separator
          const dateContainer = document.createElement("div");
          dateContainer.className = "message-date-container";
          dateContainer.innerHTML = `<div class="message-date">${formattedDate}</div>`;
          container.appendChild(dateContainer);
        }
      }
    }

    // Create and add message element
    const messageElement = createMessageElement(message);
    container.appendChild(messageElement);
  }

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

/**
 * Append only new messages without refreshing existing ones
 */
function appendNewMessages(newMessages, container) {
  for (const message of newMessages) {
    // Check for date separator
    if (message.timestamp) {
      const messageDate = new Date(message.timestamp);
      if (!isNaN(messageDate.getTime())) {
        const formattedDate = formatDate(messageDate);

        // Check if we already have this date
        const existingDates = container.querySelectorAll(".message-date");
        let hasDate = false;

        for (const date of existingDates) {
          if (date.textContent === formattedDate) {
            hasDate = true;
            break;
          }
        }

        // Add date separator if needed
        if (!hasDate) {
          const dateContainer = document.createElement("div");
          dateContainer.className = "message-date-container";
          dateContainer.innerHTML = `<div class="message-date">${formattedDate}</div>`;
          container.appendChild(dateContainer);
        }
      }
    }

    // Create message and add directly to container - no extra wrapper
    const messageElement = createMessageElement(message);
    container.appendChild(messageElement);
  }

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

/**
 * Create a message element
 */
function createMessageElement(message) {
  // Get current user ID again to ensure we have the latest
  const currentUserID = currentUserId;

  // Determine if message is outgoing (sent by current user) or incoming
  // Compare as strings to handle different types
  const isOutgoing = message.user_id.toString() === currentUserID.toString();

  // Create message container - directly create message without extra wrapper
  const messageElement = document.createElement("div");
  messageElement.className = `message ${isOutgoing ? "outgoing" : "incoming"}`;

  // Format timestamp
  let timeString = "Just now";
  if (message.timestamp) {
    const date = new Date(message.timestamp);
    if (!isNaN(date.getTime())) {
      timeString = date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    }
  }

  // Create message bubble with content
  const messageBubble = document.createElement("div");
  messageBubble.className = "message-bubble";

  // Check if message has text content
  if (message.content && message.content.trim()) {
    messageBubble.textContent = message.content;
  }

  // Add image if present
  if (message.has_image === true && message.image_url) {
    // Create image element
    const imageElement = document.createElement("img");
    imageElement.className = "message-image";
    imageElement.src = message.image_url;
    imageElement.alt = "Shared image";
    imageElement.loading = "lazy";

    // Add error handler to log issues loading the image
    imageElement.onerror = function () {
      console.error("Failed to load image:", message.image_url);
      imageElement.alt = "Image failed to load";
      imageElement.classList.add("image-error");
    };

    // Add click handler to view full size image
    imageElement.addEventListener("click", () => {
      openImageViewer(message.image_url);
    });

    // Add image to message - after text if there is text
    messageBubble.appendChild(imageElement);
  } else if (message.has_image === true && !message.image_url) {
    // If message has image flag but no URL, show a placeholder
    console.warn("Message has_image=true but no image_url:", message);
    const placeholderText = document.createElement("span");
    placeholderText.className = "image-placeholder";
    placeholderText.textContent = "🖼️ Image unavailable";
    messageBubble.appendChild(placeholderText);
  }

  // Create timestamp element
  const timestamp = document.createElement("div");
  timestamp.className = "message-timestamp";
  timestamp.textContent = timeString;

  // Append elements to message container
  messageElement.appendChild(messageBubble);
  messageElement.appendChild(timestamp);

  return messageElement;
}

/**
 * Open image viewer modal
 */
function openImageViewer(imageUrl) {
  const modal = document.getElementById("imageViewerModal");
  const fullSizeImage = document.getElementById("fullSizeImage");

  if (modal && fullSizeImage) {
    fullSizeImage.src = imageUrl;
    modal.style.display = "block";

    // Close on click
    const closeBtn = modal.querySelector(".close-modal");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
      });
    }

    // Close on outside click
    window.addEventListener("click", (event) => {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    });
  }
}

/**
 * Show trade details in modal
 */
function showTradeDetails() {
    if (!window.currentTradeDetails) {
      console.warn("No trade selected");
      return;
    }
  
    const details = window.currentTradeDetails;
    const tradeModal = document.getElementById("tradeDetailsModal");
  
    // Update modal content based on offer type
    if (details.offer_type === "trade") {
      tradeModal.querySelector(".modal-content").innerHTML = `
              <span class="close-modal">&times;</span>
              <h2>Trade Details</h2>
              <div class="trade-items-container">
                  <div class="trade-item">
                      <h3>${details.isSender ? "Your Item" : "Their Item"}</h3>
                      <div class="item-image">
                          <img src="${details.isSender ? details.sender_item_image : details.receiver_item_image}" alt="${details.isSender ? details.sender_item_name : details.receiver_item_name}">
                      </div>
                      <p>${details.isSender ? details.sender_item_name : details.receiver_item_name}</p>
                  </div>
                  <div class="trade-arrow">
                      <i class="fas fa-exchange-alt"></i>
                  </div>
                  <div class="trade-item">
                      <h3>${details.isSender ? "Their Item" : "Your Item"}</h3>
                      <div class="item-image">
                          <img src="${details.isSender ? details.receiver_item_image : details.sender_item_image}" alt="${details.isSender ? details.receiver_item_name : details.sender_item_name}">
                      </div>
                      <p>${details.isSender ? details.receiver_item_name : details.sender_item_name}</p>
                  </div>
              </div>
              <div class="trade-status">
                  <p><i class="fas fa-check-circle"></i> Trade Status: ${details.status || "active"}</p>
                  <p class="trade-id">Trade ID: ${details.offerId}</p>
              </div>
              <div class="modal-actions">
                  <button class="modal-btn cancel-btn" id="cancelTradeBtn">Close</button>
              </div>
          `;
    } else if (details.offer_type === "purchase") {
      tradeModal.querySelector(".modal-content").innerHTML = `
              <span class="close-modal">&times;</span>
              <h2>Purchase Details</h2>
              <div class="trade-items-container">
                  <div class="trade-item">
                      <h3>Item Details</h3>
                      <div class="item-image">
                          <img src="${details.item_image}" alt="${details.item_name}">
                      </div>
                      <p>${details.item_name}</p>
                  </div>
              </div>
              <div class="trade-status">
                  <p><i class="fas fa-shopping-cart"></i> Trade Status: ${details.status || "pending"}</p>
                  <p class="trade-id">Purchase Offer ID: ${details.offerId}</p>
                  <p>Buyer: ${details.buyerName}</p>
                  <p>Seller: ${details.sellerName}</p>
              </div>
              <div class="modal-actions">
                  <button class="modal-btn cancel-btn" id="cancelTradeBtn">Close</button>
              </div>
          `;
    }
  
    // Show modal
    tradeModal.style.display = "block";
  
    // Set up close handlers
    setupModalCloseHandlers();
  
    // Add specific close button handler
    const cancelBtn = document.getElementById("cancelTradeBtn");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => {
        tradeModal.style.display = "none";
      });
    }
  }

/**
 * Format date for message separators
 */
function formatDate(date) {
  const now = new Date();
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  // Check if date is today
  if (date.toDateString() === now.toDateString()) {
    return "Today";
  }

  // Check if date is yesterday
  if (date.toDateString() === yesterday.toDateString()) {
    return "Yesterday";
  }

  // Otherwise return formatted date
  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Start polling for updates
 */
function startPolling() {
  setInterval(async () => {
    try {
      // Periodically refresh the current user ID
      await refreshCurrentUserId();

      // Only check for updates to active chat
      if (currentOfferId) {
        // Check for new messages without refreshing the entire list
        const latestTimestamp = messageTimestamps[currentOfferId] || 0;
        const newMessages = await fetchNewMessages(
          currentOfferId,
          latestTimestamp
        );

        if (newMessages.length > 0) {
          // Get messages container
          const messagesContainer = document.getElementById("chatMessages");
          if (messagesContainer) {
            // Add new messages without refreshing everything
            appendNewMessages(newMessages, messagesContainer);

            // Update our cached message list
            if (loadedMessages[currentOfferId]) {
              loadedMessages[currentOfferId] = [
                ...loadedMessages[currentOfferId],
                ...newMessages,
              ];
            } else {
              loadedMessages[currentOfferId] = newMessages;
            }

            // Update the latest timestamp
            messageTimestamps[currentOfferId] = Math.max(
              messageTimestamps[currentOfferId] || 0,
              ...newMessages.map((m) => m.timestamp || 0)
            );
          }
        }
      }

      // Check for new chats without affecting current chat
      await updateChatList();
    } catch (error) {
      console.error(`Error in polling: ${error.message}`);
    }
  }, 5000); // Poll every 5 seconds
}

// Initialize chat when DOM is ready
document.addEventListener("DOMContentLoaded", initializeChat);

/**
 * Initialize user information
 */
async function initializeUser() {
  try {
    // Always get the current user ID from the server to ensure accuracy
    const response = await fetch("/check-session", {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      currentUserId = data.session_token;

      // Update UI with user ID
      const userIdElement = document.getElementById("userId");
      if (userIdElement) {
        userIdElement.textContent = currentUserId;
      }

      console.log(`User initialized with current session ID: ${currentUserId}`);
      return currentUserId;
    } else {
      console.warn("Failed to get user session, using fallback method");

      // Fallback: Try from localStorage as temporary solution
      currentUserId = localStorage.getItem("userId");
      if (!currentUserId) {
        // Last resort fallback
        console.warn("No user ID found, using default value");
        currentUserId = "7"; // Default ID, should be replaced with actual login
      }

      // Update UI
      const userIdElement = document.getElementById("userId");
      if (userIdElement) {
        userIdElement.textContent = currentUserId;
      }

      return currentUserId;
    }
  } catch (error) {
    console.error(`Error initializing user: ${error.message}`);

    // Emergency fallback
    currentUserId = localStorage.getItem("userId") || "7";
    console.warn(`Using fallback user ID: ${currentUserId}`);

    // Update UI
    const userIdElement = document.getElementById("userId");
    if (userIdElement) {
      userIdElement.textContent = currentUserId;
    }

    return currentUserId;
  }
}

// ==================== Event Handlers ====================
/**
 * Set up all event handlers
 */
function setupEventHandlers() {
  // Message input and send button
  const sendButton = document.getElementById("sendButton");
  const messageInput = document.getElementById("messageInput");

  if (sendButton) {
    // Remove any existing listeners
    const oldClickListener = sendButton._clickListener;
    if (oldClickListener) {
      sendButton.removeEventListener("click", oldClickListener);
    }

    // Add new listener and store reference
    sendButton._clickListener = sendMessage;
    sendButton.addEventListener("click", sendButton._clickListener);
  }

  if (messageInput) {
    // Remove any existing listeners
    const oldKeyListener = messageInput._keyListener;
    if (oldKeyListener) {
      messageInput.removeEventListener("keypress", oldKeyListener);
    }

    // Create keypress handler
    const keypressHandler = (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    };

    // Add new listener and store reference
    messageInput._keyListener = keypressHandler;
    messageInput.addEventListener("keypress", messageInput._keyListener);
  }

  // Trade view button
  const viewTradeBtn = document.getElementById("viewTradeBtn");
  if (viewTradeBtn) {
    viewTradeBtn.addEventListener("click", showTradeDetails);
  }

  // Image upload functionality
  const imageUpload = document.getElementById("imageUpload");
  if (imageUpload) {
    imageUpload.addEventListener("change", handleImageSelect);
  }

  // Remove image button
  const removeImageBtn = document.getElementById("removeImageBtn");
  if (removeImageBtn) {
    removeImageBtn.addEventListener("click", removeSelectedImage);
  }

  // Search functionality
  const searchInput = document.querySelector(".search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (event) => {
      const searchTerm = event.target.value.toLowerCase();
      const chatItems = document.querySelectorAll(".chat-item");

      chatItems.forEach((item) => {
        const nameElem = item.querySelector(".chat-name");
        if (!nameElem) return;

        const name = nameElem.textContent.toLowerCase();
        if (!searchTerm || name.includes(searchTerm)) {
          item.style.display = "flex";
        } else {
          item.style.display = "none";
        }
      });
    });
  }

  // Modal close handlers - set up when modal is shown
  setupModalCloseHandlers();
}

/**
 * Handle image selection for upload
 */
function handleImageSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Check file type
  if (!file.type.match("image.*")) {
    alert("Please select an image file");
    event.target.value = "";
    return;
  }

  // Check file size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    alert("Image size should be less than 5MB");
    event.target.value = "";
    return;
  }

  // Read the file
  const reader = new FileReader();
  reader.onload = function (e) {
    // Store the base64 data
    currentImageData = e.target.result;

    // Show preview
    const previewContainer = document.getElementById("imagePreviewContainer");
    const preview = document.getElementById("imagePreview");

    if (previewContainer && preview) {
      preview.innerHTML = `<img src="${currentImageData}" alt="Selected image">`;
      previewContainer.classList.add("visible");
    }
  };

  reader.readAsDataURL(file);
}

/**
 * Remove the selected image
 */
function removeSelectedImage() {
  // Clear the image data
  currentImageData = null;

  // Hide preview
  const previewContainer = document.getElementById("imagePreviewContainer");
  const preview = document.getElementById("imagePreview");
  const fileInput = document.getElementById("imageUpload");

  if (previewContainer) {
    previewContainer.classList.remove("visible");
  }

  if (preview) {
    preview.innerHTML = "";
  }

  if (fileInput) {
    fileInput.value = "";
  }
}

/**
 * Set up modal close handlers
 */
function setupModalCloseHandlers() {
  // Trade details modal
  const tradeModal = document.getElementById("tradeDetailsModal");
  if (tradeModal) {
    const closeBtn = tradeModal.querySelector(".close-modal");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        tradeModal.style.display = "none";
      });
    }

    // Close on outside click
    window.addEventListener("click", (event) => {
      if (event.target === tradeModal) {
        tradeModal.style.display = "none";
      }
    });
  }

  // Image viewer modal
  const imageModal = document.getElementById("imageViewerModal");
  if (imageModal) {
    const closeBtn = imageModal.querySelector(".close-modal");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        imageModal.style.display = "none";
      });
    }

    // Close on outside click
    window.addEventListener("click", (event) => {
      if (event.target === imageModal) {
        imageModal.style.display = "none";
      }
    });
  }
}

// ==================== API Interactions ====================
/**
 * Fetch accepted trade offers from API
 */
async function fetchOffers() {
  try {
    const response = await fetch("/chat/accepted-offers", {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const offers = await response.json();
      console.log("Fetched offers:", offers);
      return offers;
    }

    console.warn("Failed to fetch offers:", response.status);
    return [];
  } catch (error) {
    console.error(`Error fetching offers: ${error.message}`);
    return [];
  }
}

/**
 * Fetch all messages for a chat room
 */
async function fetchMessages(offerId) {
  try {
    const response = await fetch(`/chat/messages/${offerId}`, {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      return data.messages || [];
    }

    console.warn(
      `Failed to fetch messages for offer ${offerId}:`,
      response.status
    );
    return [];
  } catch (error) {
    console.error(`Error fetching messages: ${error.message}`);
    return [];
  }
}

/**
 * Fetch only new messages since timestamp
 */
async function fetchNewMessages(offerId, sinceTimestamp) {
  try {
    const response = await fetch(`/chat/messages/${offerId}`, {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      const allMessages = data.messages || [];

      // Filter to only get messages newer than the timestamp
      return allMessages.filter((msg) => (msg.timestamp || 0) > sinceTimestamp);
    }

    console.warn(
      `Failed to fetch new messages for offer ${offerId}:`,
      response.status
    );
    return [];
  } catch (error) {
    console.error(`Error fetching new messages: ${error.message}`);
    return [];
  }
}

/**
 * Send a message to the current chat
 */
async function sendMessage() {
  if (!currentOfferId) {
    console.warn("No chat selected");
    return;
  }

  const input = document.getElementById("messageInput");
  if (!input) return;

  const messageText = input.value.trim();

  // Check if we have either text or image
  if (!messageText && !currentImageData) {
    console.warn("No message content or image to send");
    return;
  }

  // Prevent double-sending by checking if message is already being sent
  if (isMessageSending) {
    console.warn("Message already being sent, please wait");
    return;
  }

  // Set sending flag
  isMessageSending = true;

  // Disable input and button while sending to prevent double-sending
  input.disabled = true;
  const sendButton = document.getElementById("sendButton");
  if (sendButton) sendButton.disabled = true;

  try {
    // Make sure we have the latest user ID
    await refreshCurrentUserId();

    // Clear input field immediately to prevent accidental double-send
    const originalText = messageText;
    input.value = "";

    // Generate a temporary message ID for local display
    const tempMessageId = `temp_${Date.now()}`;

    // Prepare data for display
    const tempContent = originalText || (currentImageData ? "" : "");

    // Add to UI immediately for better experience
    const messagesContainer = document.getElementById("chatMessages");
    if (messagesContainer) {
      const tempMessage = {
        id: tempMessageId,
        user_id: currentUserId,
        content: tempContent,
        timestamp: Date.now(),
        has_image: !!currentImageData,
        image_url: currentImageData, // This won't be rendered directly as URL but shows intent
      };

      // Create message element directly without wrapper
      const messageElement = createMessageElement(tempMessage);
      messageElement.classList.add("sending"); // Add sending class for visual feedback
      messageElement.setAttribute("data-temp-id", tempMessageId);
      messagesContainer.appendChild(messageElement);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Prepare data to send
    const messageData = {
      message: originalText,
    };

    // Add image if present
    if (currentImageData) {
      messageData.image = currentImageData;
    }

    // Send to server
    console.log(`Sending message to offer ${currentOfferId}`);

    const response = await fetch(`/chat/send-message/${currentOfferId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(messageData),
    });

    // Check response
    if (response.ok) {
      console.log("Message sent successfully");
      // Remove selected image and preview
      removeSelectedImage();

      // Update our message cache with the server response
      const responseData = await response.json();

      // Remove temporary message and replace with real one from the server
      const serverMessage = responseData.data;
      if (serverMessage) {
        // Find and remove the temporary message to prevent duplicates
        const tempMsg = messagesContainer.querySelector(
          `[data-temp-id="${tempMessageId}"]`
        );
        if (tempMsg) {
          tempMsg.remove();
        }

        // Add the server's version of the message which has correct image URLs
        const serverMessageElement = createMessageElement(serverMessage);
        messagesContainer.appendChild(serverMessageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Update message cache
        if (loadedMessages[currentOfferId]) {
          loadedMessages[currentOfferId].push(serverMessage);
        } else {
          loadedMessages[currentOfferId] = [serverMessage];
        }

        // Update timestamp
        if (serverMessage.timestamp) {
          messageTimestamps[currentOfferId] = Math.max(
            messageTimestamps[currentOfferId] || 0,
            serverMessage.timestamp
          );
        }
      } else {
        // If we don't get a proper response, force refresh messages
        await loadChatMessages(currentOfferId, true);
      }
    } else {
      console.error("Failed to send message", await response.text());
      alert("Failed to send message. Please try again.");

      // If it failed, we can put the text back in the input
      input.value = originalText;

      // Remove the temporary message
      const tempMsg = messagesContainer.querySelector(
        `[data-temp-id="${tempMessageId}"]`
      );
      if (tempMsg) {
        tempMsg.remove();
      }
    }
  } catch (error) {
    console.error(`Error sending message: ${error.message}`);
    alert("Error sending message. Please try again.");

    // Remove temp message on error
    const messagesContainer = document.getElementById("chatMessages");
    if (messagesContainer) {
      const tempMsgs = messagesContainer.querySelectorAll(".message.sending");
      tempMsgs.forEach((msg) => msg.remove());
    }
  } finally {
    // Re-enable input whether success or failure
    input.disabled = false;
    if (sendButton) sendButton.disabled = false;

    // Reset sending flag
    isMessageSending = false;
  }
}

/**
 * Refresh the current user ID from the server
 */
async function refreshCurrentUserId() {
  try {
    const response = await fetch("/check-session", {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      if (data.session_token) {
        // Check if the user ID has changed
        const oldUserId = currentUserId;
        const newUserId = data.session_token;

        if (oldUserId !== newUserId) {
          console.log(`User ID changed from ${oldUserId} to ${newUserId}`);
          currentUserId = newUserId;

          // Update UI
          const userIdElement = document.getElementById("userId");
          if (userIdElement) {
            userIdElement.textContent = currentUserId;
          }

          // Force a refresh of the current chat display if a chat is open
          if (currentOfferId) {
            loadChatMessages(currentOfferId, true);
          }

          // Clear message cache to ensure proper message alignment
          loadedMessages = {};
          messageTimestamps = {};
        }
      }
    }
  } catch (error) {
    console.warn(`Error refreshing user ID: ${error.message}`);
  }
}

// ==================== UI Updates ====================
/**
 * Update the list of chat rooms
 */
async function updateChatList() {
  try {
    // Get the chat list element
    const chatList = document.getElementById("chatList");
    if (!chatList) return;

    // Fetch offers from API
    const offers = await fetchOffers();
    chatRooms = offers;

    // Save current scroll position
    const scrollPosition = chatList.scrollTop;

    // Clear and rebuild the chat list
    chatList.innerHTML = "";

    if (offers.length === 0) {
      chatList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-comments"></i>
                        <p>No active conversations</p>
                    </div>
                `;
      return;
    }

    // Add each offer as a chat item
    for (const offer of offers) {
      const chatItem = createChatListItem(offer);
      chatList.appendChild(chatItem);
    }

    // Select first chat if none selected
    // In the updateChatList() function, modify the line that selects the first chat
    if (!currentOfferId && offers.length > 0) {
      const firstOffer = offers[0];
      openChat(
        firstOffer.offer_id,
        firstOffer.other_user_name || "User",
        firstOffer.offer_type || "trade"
      );

      // Reset currentTradeDetails
      window.currentTradeDetails = null;
    }

    // Restore scroll position
    chatList.scrollTop = scrollPosition;
  } catch (error) {
    console.error(`Error updating chat list: ${error.message}`);
    const chatList = document.getElementById("chatList");
    if (chatList) {
      chatList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Error loading chats</p>
                    </div>
                `;
    }
  }
}

/**
 * Create a chat list item element
 */
/**
 * Create a chat list item element
 */
/**
 * Create a chat list item element
 */
/**
 * Create a chat list item element
 */
function createChatListItem(offer) {
  const offerId = offer.offer_id.toString();
  const isActive = currentOfferId === offerId;
  const hasUnread = offer.unread_count > 0;

  // Determine offer type (trade or purchase)
  const offerType = offer.offer_type || "trade"; // Default to trade if not specified

  // Determine the correct item image and name for trade and purchase
  let itemImage, itemName;
  if (offerType === "trade") {
    // For trade, show the item you'll receive
    if (offer.is_sender) {
      // If you're the sender, show the receiver's item
      itemImage = offer.receiver_item_image || "/static/image_test/camera.jpg";
      itemName = offer.receiver_item_name || "Trade Item";
    } else {
      // If you're the receiver, show the sender's item
      itemImage = offer.sender_item_image || "/static/image_test/camera.jpg";
      itemName = offer.sender_item_name || "Trade Item";
    }
  } else {
    // For purchase, show the item being purchased
    itemImage = offer.item_image || "/static/image_test/camera.jpg";
    itemName = offer.item_name || "Purchase Item";
  }

  const item = document.createElement("div");
  item.className = `chat-item ${isActive ? "active" : ""} ${offerType}-offer`;
  item.setAttribute("data-offer-id", offerId);
  item.setAttribute("data-offer-type", offerType);

  // Format timestamp
  let timeDisplay = "New";
  if (offer.created_at) {
    const date = new Date(offer.created_at);
    if (!isNaN(date.getTime())) {
      const now = new Date();
      const diff = now - date;

      if (diff < 60000) {
        timeDisplay = "Now";
      } else if (diff < 3600000) {
        timeDisplay = `${Math.floor(diff / 60000)}m ago`;
      } else if (diff < 86400000) {
        timeDisplay = `${Math.floor(diff / 3600000)}h ago`;
      } else {
        timeDisplay = `${Math.floor(diff / 86400000)}d ago`;
      }
    }
  }

  // Get preview text 
  let previewText = `${
    offerType.charAt(0).toUpperCase() + offerType.slice(1)
  } #${offerId}`;

  item.innerHTML = `
    <div class="avatar">
      <img src="${itemImage}" alt="${itemName}">
    </div>
    <div class="chat-info">
      <div class="chat-name">${itemName}</div>
      <div class="chat-preview">${previewText}</div>
    </div>
    <div class="chat-meta">
      <div class="timestamp">${timeDisplay}</div>
      ${hasUnread ? `<div class="unread-badge">${offer.unread_count}</div>` : ""}
    </div>
    <div class="offer-type-badge ${offerType}">${offerType}</div>
  `;

  // Add click handler with offer type
  item.addEventListener("click", () => {
    openChat(offerId, itemName, offerType);
  });

  return item;
}

async function openChat(offerId, itemName, offerType) {
  console.log(
    `Opening chat: ${offerId} for ${itemName}, Type: ${offerType}`
  );

  // Clear previous chat messages
  const messagesContainer = document.getElementById("chatMessages");
  if (messagesContainer) {
    messagesContainer.innerHTML = `
            <div class="loading-messages">
                <i class="fas fa-spinner fa-spin"></i> Loading messages...
            </div>
        `;
  }

  // Update current state
  currentOfferId = offerId;
  currentChatPartner = itemName;

  // Update UI - set active chat item
  document.querySelectorAll(".chat-item").forEach((item) => {
    item.classList.remove("active");
    if (
      item.getAttribute("data-offer-id") === offerId.toString() &&
      item.getAttribute("data-offer-type") === offerType
    ) {
      item.classList.add("active");
    }
  });

  // Update chat header
  const headerName = document.getElementById("chatHeaderName");
  const headerInfo = document.getElementById("chatHeaderInfo");

  if (headerName) headerName.textContent = itemName;

  // Prepare status update UI
  const statusSelect = document.getElementById("tradeStatusSelect");
  const updateStatusBtn = document.getElementById("updateStatusBtn");
  const viewTradeBtn = document.getElementById("viewTradeBtn");

  // Determine which status endpoint to use
  let statusEndpoint =
    offerType === "trade"
      ? `/trade-offers/${offerId}/match-status`
      : `/purchase-offers/${offerId}/status`;

  try {
    // Fetch current status
    const response = await fetch(statusEndpoint, {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const statusData = await response.json();
      const currentStatus = statusData.status;

      // Configure status select and button based on offer type
      if (statusSelect) {
        if (offerType === "trade") {
          // Trade offer status options
          statusSelect.innerHTML = `
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                    `;
        } else {
          // Purchase offer status options
          statusSelect.innerHTML = `
                        <option value="pending">Pending</option>
                        <option value="accepted">Accepted</option>
                        <option value="rejected">Rejected</option>
                    `;
        }

        // Set current status
        statusSelect.value = currentStatus;
        statusSelect.disabled = false;
      }

      // Enable buttons
      if (updateStatusBtn) updateStatusBtn.disabled = false;
      if (viewTradeBtn) viewTradeBtn.disabled = false;

      // Add status message to chat
      if (messagesContainer) {
        const systemMessage = document.createElement("div");
        systemMessage.className = "message-date-container";

        let statusMessage = "";
        if (offerType === "trade") {
          statusMessage = getTradeStatusMessage(currentStatus);
        } else {
          statusMessage = getPurchaseStatusMessage(currentStatus);
        }

        systemMessage.innerHTML = `
                    <div class="message-date system-message ${currentStatus}-status">
                        ${statusMessage}
                    </div>
                `;
        messagesContainer.appendChild(systemMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    } else {
      console.warn(`Failed to get ${offerType} status:`, await response.text());
    }
  } catch (error) {
    console.error(`Error fetching ${offerType} status:`, error);
  }

  // Load chat messages
  await loadChatMessages(offerId, true);

  // Update trade details data for view trade button
  updateTradeDetailsData(offerId, offerType);
}

function getTradeStatusMessage(status) {
  switch (status) {
    case "active":
      return "This trade is currently active.";
    case "completed":
      return "This trade has been completed. Items have been exchanged.";
    case "cancelled":
      return "This trade has been cancelled.";
    default:
      return "Trade status unknown.";
  }
}

function getPurchaseStatusMessage(status) {
  switch (status) {
    case "pending":
      return "This purchase offer is pending review.";
    case "accepted":
      return "This purchase offer has been accepted.";
    case "rejected":
      return "This purchase offer has been rejected.";
    default:
      return "Purchase offer status unknown.";
  }
}

async function updateTradeStatus() {
  console.log("Update status button clicked");

  if (!currentOfferId) {
    console.warn("No chat selected");
    return;
  }

  const statusSelect = document.getElementById("tradeStatusSelect");
  if (!statusSelect) {
    console.warn("Status select not found");
    return;
  }

  const newStatus = statusSelect.value;
  console.log(`Attempting to update status to: ${newStatus}`);

  // Determine which endpoint to use based on the current offer type
  const offerType = getCurrentOfferType();

  // Construct the appropriate endpoint
  const statusEndpoint =
    offerType === "trade"
      ? `/trade-offers/${currentOfferId}/status`
      : `/purchase-offers/${currentOfferId}/status`;

  // Confirm before final status changes
  if (newStatus !== (offerType === "trade" ? "active" : "pending")) {
    const confirmAction = confirm(
      `Are you sure you want to mark this ${offerType} as ${newStatus}? This action cannot be undone.`
    );
    if (!confirmAction) return;
  }

  try {
    // Show user feedback
    const updateBtn = document.getElementById("updateStatusBtn");
    if (updateBtn) {
      updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
      updateBtn.disabled = true;
    }

    // Send update to server
    const response = await fetch(statusEndpoint, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ status: newStatus }),
    });

    console.log(`Server response status: ${response.status}`);

    if (response.ok) {
      // Success
      const data = await response.json();
      console.log("Status updated successfully:", data);

      // Add system message to chat
      const messagesContainer = document.getElementById("chatMessages");
      if (messagesContainer) {
        const systemMessage = document.createElement("div");
        systemMessage.className = "message-date-container";

        let statusMessage = "";
        if (offerType === "trade") {
          statusMessage = getTradeStatusMessage(newStatus);
        } else {
          statusMessage = getPurchaseStatusMessage(newStatus);
        }

        systemMessage.innerHTML = `<div class="message-date system-message ${newStatus}-status">${statusMessage}</div>`;
        messagesContainer.appendChild(systemMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }

      // Show alert
      alert(
        `${
          offerType.charAt(0).toUpperCase() + offerType.slice(1)
        } status updated to: ${newStatus}`
      );

      // Optionally update the UI to reflect the new status
      updateUIAfterStatusChange(newStatus, offerType);
    } else {
      // Handle error
      console.error("Failed to update status:", await response.text());
      alert(`Failed to update ${offerType} status. Please try again.`);
    }
  } catch (error) {
    console.error(`Error updating ${offerType} status: ${error.message}`);
    alert(`Error updating ${offerType} status: ${error.message}`);
  } finally {
    // Reset button
    const updateBtn = document.getElementById("updateStatusBtn");
    if (updateBtn) {
      updateBtn.innerHTML = '<i class="fas fa-check"></i> Update Status';
      updateBtn.disabled = false;
    }
  }
}

function getCurrentOfferType() {
  // This function determines the current offer type based on the available UI elements
  const viewTradeBtn = document.getElementById("viewTradeBtn");

  // If viewTradeBtn exists, check for current trade details
  if (viewTradeBtn && window.currentTradeDetails) {
    return window.currentTradeDetails.offer_type || "trade";
  }

  // Fallback to checking chat header or other indicators
  const chatHeaderInfo = document.getElementById("chatHeaderInfo");
  if (chatHeaderInfo) {
    const infoText = chatHeaderInfo.textContent.toLowerCase();
    if (infoText.includes("trade")) return "trade";
    if (infoText.includes("purchase")) return "purchase";
  }

  // Default to trade if no clear indication
  return "trade";
}

function updateUIAfterStatusChange(newStatus, offerType) {
  // Update status select to reflect the new status
  const statusSelect = document.getElementById("tradeStatusSelect");
  if (statusSelect) {
    statusSelect.value = newStatus;
  }

  // Potentially disable certain actions based on status
  const updateStatusBtn = document.getElementById("updateStatusBtn");
  const viewTradeBtn = document.getElementById("viewTradeBtn");
  const sendButton = document.getElementById("sendButton");
  const messageInput = document.getElementById("messageInput");

  if (offerType === "trade") {
    // For trade offers
    if (newStatus === "cancelled" || newStatus === "completed") {
      // Disable message sending if trade is completed or cancelled
      if (sendButton) sendButton.disabled = true;
      if (messageInput) messageInput.disabled = true;
    } else {
      // Re-enable if active
      if (sendButton) sendButton.disabled = false;
      if (messageInput) messageInput.disabled = false;
    }
  } else if (offerType === "purchase") {
    // For purchase offers
    if (newStatus === "rejected") {
      // Disable message sending if purchase is rejected
      if (sendButton) sendButton.disabled = true;
      if (messageInput) messageInput.disabled = true;
    } else {
      // Re-enable if pending or accepted
      if (sendButton) sendButton.disabled = false;
      if (messageInput) messageInput.disabled = false;
    }
  }
}

function showTradeDetails() {
    if (!window.currentTradeDetails) {
      console.warn("No trade selected");
      return;
    }
  
    const details = window.currentTradeDetails;
    const tradeModal = document.getElementById("tradeDetailsModal");
  
    // Update modal content based on offer type
    if (details.offer_type === "trade") {
      tradeModal.querySelector(".modal-content").innerHTML = `
              <span class="close-modal">&times;</span>
              <h2>Trade Details</h2>
              <div class="trade-items-container">
                  <div class="trade-item">
                      <h3>Your Item</h3>
                      <div class="item-image">
                          <img src="${details.isSender ? details.sender_item_image : details.receiver_item_image}" alt="${details.isSender ? details.sender_item_name : details.receiver_item_name}">
                      </div>
                      <p>${details.isSender ? details.sender_item_name : details.receiver_item_name}</p>
                  </div>
                  <div class="trade-arrow">
                      <i class="fas fa-exchange-alt"></i>
                  </div>
                  <div class="trade-item">
                      <h3>Their Item</h3>
                      <div class="item-image">
                          <img src="${details.isSender ? details.receiver_item_image : details.sender_item_image}" alt="${details.isSender ? details.receiver_item_name : details.sender_item_name}">
                      </div>
                      <p>${details.isSender ? details.receiver_item_name : details.sender_item_name}</p>
                  </div>
              </div>
              <div class="trade-status">
                  <p><i class="fas fa-check-circle"></i> Trade Status: ${details.status || "active"}</p>
                  <p class="trade-id">Trade ID: ${details.offerId}</p>
              </div>
              <div class="modal-actions">
                  <button class="modal-btn cancel-btn" id="cancelTradeBtn">Close</button>
              </div>
          `;
    } else if (details.offer_type === "purchase") {
      tradeModal.querySelector(".modal-content").innerHTML = `
              <span class="close-modal">&times;</span>
              <h2>Purchase Details</h2>
              <div class="trade-items-container">
                  <div class="trade-item">
                      <h3>Item Details</h3>
                      <div class="item-image">
                          <img src="${details.item_image}" alt="${details.item_name}">
                      </div>
                      <p>${details.item_name}</p>
                  </div>
              </div>
              <div class="trade-status">
                  <p><i class="fas fa-shopping-cart"></i> Trade Status: ${details.status || "pending"}</p>
                  <p class="trade-id">Purchase Offer ID: ${details.offerId}</p>
                  <p>Buyer: ${details.buyerName}</p>
                  <p>Seller: ${details.sellerName}</p>
              </div>
              <div class="modal-actions">
                  <button class="modal-btn cancel-btn" id="cancelTradeBtn">Close</button>
              </div>
          `;
    }
  
    // Show modal
    tradeModal.style.display = "block";
  
    // Set up close handlers
    setupModalCloseHandlers();
  
    // Add specific close button handler
    const cancelBtn = document.getElementById("cancelTradeBtn");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", () => {
        tradeModal.style.display = "none";
      });
    }
  }

function updateTradeDetailsData(offerId, offerType) {
    console.log("Updating trade details for:", offerId, offerType);
    
    // Find the offer in chatRooms
    const offerData = chatRooms.find(offer => 
        offer.offer_id.toString() === offerId.toString() && 
        offer.offer_type === offerType
    );
    
    console.log("Found offer data:", offerData);
    
    if (!offerData) {
        console.error(`No offer data found for ID: ${offerId}, type: ${offerType}`);
        return;
    }
    
    if (offerType === "trade") {
        // Trade offer details logic
        window.currentTradeDetails = {
            offerId: offerId,
            offer_type: "trade",
            isSender: offerData.is_sender,
            
            // Store both item IDs
            senderItemId: offerData.sender_item_id,
            receiverItemId: offerData.receiver_item_id,
            
            // Store both item names
            sender_item_name: offerData.sender_item_name || "Unnamed Item",
            receiver_item_name: offerData.receiver_item_name || "Unnamed Item",
            
            // Store both item images
            sender_item_image: offerData.sender_item_image || "/static/image_test/camera.jpg",
            receiver_item_image: offerData.receiver_item_image || "/static/image_test/guitar.jpg",
            
            // Add status with fallback
            status: offerData.status || "active",
            
            // Add detailed status information
            statusText: getTradeStatusText(offerData.status || "active"),
            statusClass: offerData.status || "active"
        };
    } else if (offerType === "purchase") {
        // Purchase offer details logic
        window.currentTradeDetails = {
            offerId: offerId,
            offer_type: "purchase",
            itemId: offerData.item_id,
            
            // Store item name and image
            item_name: offerData.item_name || "Unnamed Item",
            item_image: offerData.item_image || "/static/image_test/camera.jpg",
            
            // Add status with fallback
            status: offerData.status || "pending",
            
            // Add detailed status information
            statusText: getPurchaseStatusText(offerData.status || "pending"),
            statusClass: offerData.status || "pending",
            buyerName: offerData.is_buyer ? "You" : offerData.other_user_name,
            sellerName: offerData.is_buyer ? offerData.other_user_name : "You"
        };
    }
    
    console.log("Final trade details:", window.currentTradeDetails);
  }

// Helper functions for status text
function getTradeStatusText(status) {
  switch(status) {
      case "active":
          return "Trade in progress";
      case "completed":
          return "Trade completed";
      case "cancelled":
          return "Trade cancelled";
      default:
          return "Unknown status";
  }
}

function getPurchaseStatusText(status) {
  switch(status) {
      case "pending":
          return "Purchase pending";
      case "accepted":
          return "Purchase accepted";
      case "rejected":
          return "Purchase rejected";
      default:
          return "Unknown status";
  }
}

// Event Handlers ====================
/**
 * Set up all event handlers
 */
function setupEventHandlers() {
  // Message input and send button
  const sendButton = document.getElementById("sendButton");
  const messageInput = document.getElementById("messageInput");

  if (sendButton) {
    // Remove any existing listeners
    const oldClickListener = sendButton._clickListener;
    if (oldClickListener) {
      sendButton.removeEventListener("click", oldClickListener);

      /**
       * Update the trade status
       */
      async function updateTradeStatus() {
        if (!currentOfferId) {
          console.warn("No chat selected");
          return;
        }

        const statusSelect = document.getElementById("tradeStatusSelect");
        if (!statusSelect) return;

        const newStatus = statusSelect.value;

        // Confirm before completing or cancelling
        if (newStatus !== "active") {
          const confirmAction = confirm(
            `Are you sure you want to mark this trade as ${newStatus}? This action cannot be undone.`
          );
          if (!confirmAction) return;
        }

        try {
          // Disable UI while updating
          statusSelect.disabled = true;
          const updateBtn = document.getElementById("updateStatusBtn");
          if (updateBtn) updateBtn.disabled = true;

          // Send update to server
          const response = await fetch(
            `/trade-offers/${currentOfferId}/status`,
            {
              method: "PUT",
              headers: {
                "Content-Type": "application/json",
              },
              credentials: "include",
              body: JSON.stringify({ status: newStatus }),
            }
          );

          if (response.ok) {
            // Success - show a message to the user
            const data = await response.json();
            console.log("Status updated successfully:", data);

            // Add system message to chat
            const messagesContainer = document.getElementById("chatMessages");
            if (messagesContainer) {
              const systemMessage = document.createElement("div");
              systemMessage.className = "message-date-container";

              let statusMessage = "";
              if (newStatus === "completed") {
                statusMessage =
                  "This trade has been marked as completed. Items have been exchanged.";
              } else if (newStatus === "cancelled") {
                statusMessage =
                  "This trade has been cancelled. No items were exchanged.";
              } else {
                statusMessage = "This trade is now active.";
              }

              systemMessage.innerHTML = `<div class="message-date system-message ${newStatus}-status">${statusMessage}</div>`;
              messagesContainer.appendChild(systemMessage);
              messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            // Keep the status select updated
            statusSelect.value = newStatus;

            // Show a popup notification
            showNotification(`Trade status updated to: ${newStatus}`);
          } else {
            // Handle error
            console.error("Failed to update status:", await response.text());
            alert("Failed to update trade status. Please try again.");
          }
        } catch (error) {
          console.error(`Error updating trade status: ${error.message}`);
          alert("Error updating trade status. Please try again.");
        } finally {
          // Re-enable UI
          statusSelect.disabled = false;
          const updateBtn = document.getElementById("updateStatusBtn");
          if (updateBtn) updateBtn.disabled = true; // Keep disabled until next change
        }
      }

      /**
       * Show a temporary notification
       */
      function showNotification(message, duration = 3000) {
        // Create notification element if it doesn't exist
        let notification = document.getElementById("statusNotification");

        if (!notification) {
          notification = document.createElement("div");
          notification.id = "statusNotification";
          notification.className = "status-notification";
          document.body.appendChild(notification);
        }

        // Update and show the notification
        notification.textContent = message;
        notification.classList.add("visible");

        // Hide after duration
        setTimeout(() => {
          notification.classList.remove("visible");
        }, duration);
      }
    }

    // Add new listener and store reference
    sendButton._clickListener = sendMessage;
    sendButton.addEventListener("click", sendButton._clickListener);
  }

  if (messageInput) {
    // Remove any existing listeners
    const oldKeyListener = messageInput._keyListener;
    if (oldKeyListener) {
      messageInput.removeEventListener("keypress", oldKeyListener);
    }

    // Create keypress handler
    const keypressHandler = (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    };

    // Add new listener and store reference
    messageInput._keyListener = keypressHandler;
    messageInput.addEventListener("keypress", messageInput._keyListener);
  }

  // Trade view button
  const viewTradeBtn = document.getElementById("viewTradeBtn");
  if (viewTradeBtn) {
    viewTradeBtn.addEventListener("click", showTradeDetails);
  }

  // Trade status update button
  const updateStatusBtn = document.getElementById("updateStatusBtn");
  if (updateStatusBtn) {
    updateStatusBtn.addEventListener("click", updateTradeStatus);
  }

  // Trade status select change handler
  const statusSelect = document.getElementById("tradeStatusSelect");
  if (statusSelect) {
    statusSelect.addEventListener("change", function () {
      // Enable update button when status changes
      const updateBtn = document.getElementById("updateStatusBtn");
      if (updateBtn) {
        updateBtn.disabled = false;
      }
    });
  }

  // Image upload functionality
  const imageUpload = document.getElementById("imageUpload");
  if (imageUpload) {
    imageUpload.addEventListener("change", handleImageSelect);
  }

  // Remove image button
  const removeImageBtn = document.getElementById("removeImageBtn");
  if (removeImageBtn) {
    removeImageBtn.addEventListener("click", removeSelectedImage);
  }

  // Search functionality
  const searchInput = document.querySelector(".search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (event) => {
      const searchTerm = event.target.value.toLowerCase();
      const chatItems = document.querySelectorAll(".chat-item");

      chatItems.forEach((item) => {
        const nameElem = item.querySelector(".chat-name");
        if (!nameElem) return;

        const name = nameElem.textContent.toLowerCase();
        if (!searchTerm || name.includes(searchTerm)) {
          item.style.display = "flex";
        } else {
          item.style.display = "none";
        }
      });
    });
  }

  // Add this at the end of the file, ensuring it's properly enclosed in scope

  /**
   * Update the trade status
   */
  async function updateTradeStatus() {
    console.log("Update status button clicked");

    if (!currentOfferId) {
      console.warn("No chat selected");
      return;
    }

    const statusSelect = document.getElementById("tradeStatusSelect");
    if (!statusSelect) {
      console.warn("Status select not found");
      return;
    }

    const newStatus = statusSelect.value;
    console.log(`Attempting to update status to: ${newStatus}`);

    // Confirm before completing or cancelling
    if (newStatus !== "active") {
      const confirmAction = confirm(
        `Are you sure you want to mark this trade as ${newStatus}? This action cannot be undone.`
      );
      if (!confirmAction) return;
    }

    try {
      // Show user feedback
      const updateBtn = document.getElementById("updateStatusBtn");
      if (updateBtn) {
        updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        updateBtn.disabled = true;
      }

      // Send update to server
      const response = await fetch(`/trade-offers/${currentOfferId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ status: newStatus }),
      });

      console.log(`Server response status: ${response.status}`);

      if (response.ok) {
        // Success
        const data = await response.json();
        console.log("Status updated successfully:", data);

        // Add system message to chat
        const messagesContainer = document.getElementById("chatMessages");
        if (messagesContainer) {
          const systemMessage = document.createElement("div");
          systemMessage.className = "message-date-container";

          let statusMessage = "";
          if (newStatus === "completed") {
            statusMessage =
              "This trade has been marked as completed. Items have been exchanged.";
          } else if (newStatus === "cancelled") {
            statusMessage =
              "This trade has been cancelled. No items were exchanged.";
          } else {
            statusMessage = "This trade is now active.";
          }

          systemMessage.innerHTML = `<div class="message-date system-message ${newStatus}-status">${statusMessage}</div>`;
          messagesContainer.appendChild(systemMessage);
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Show alert
        alert(`Trade status updated to: ${newStatus}`);
      } else {
        // Handle error
        console.error("Failed to update status:", await response.text());
        alert("Failed to update trade status. Please try again.");
      }
    } catch (error) {
      console.error(`Error updating trade status: ${error.message}`);
      alert(`Error updating trade status: ${error.message}`);
    } finally {
      // Reset button
      const updateBtn = document.getElementById("updateStatusBtn");
      if (updateBtn) {
        updateBtn.innerHTML = '<i class="fas fa-check"></i> Update Status';
        updateBtn.disabled = false;
      }
    }
  }

  // Modal close handlers - set up when modal is shown
  setupModalCloseHandlers();
}