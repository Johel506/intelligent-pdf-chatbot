// frontend/src/services/api.js
import axios from 'axios';

// This is the base URL of our FastAPI backend
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

/**
 * Sends a message to the backend's /chat endpoint.
 * @param {string} message The user's message.
 * @param {string} conversationId The current session ID.
 * @returns {Promise<string>} The AI's response message.
 */
export const sendMessage = async (message, conversationId) => {
  try {
    const payload = {
      message: message,
      conversation_id: conversationId,
    };
    // This makes the POST request to http://127.0.0.1:8000/chat
    const response = await apiClient.post('/chat', payload);
    return response.data.response;
  } catch (error) {
    console.error("Error sending message to backend:", error);
    // Return a user-friendly error message
    return "Sorry, I couldn't connect to the AI service. Please try again later.";
  }
};