// frontend/src/services/api.js
import axios from 'axios';


const apiClient = axios.create({
  baseURL: __API_BASE_URL__, 
});

/**
 * Sends a message to the backend's /chat endpoint.
 * @param {string} message The user's message.
 * @param {string} conversationId The current session ID.
 * @returns {Promise<any>} The full response object from the backend.
 */
export const sendMessage = async (message, conversationId, options = {}) => {
  try {
    const payload = {
      message: message,
      conversation_id: conversationId,
    };
    // This makes the POST request to the configured baseURL + /chat
    const response = await apiClient.post('/chat', payload, options);
    return response;
  } catch (error) {
    console.error("Error sending message to backend:", error);
    // Re-throw the error to be handled by the calling function
    throw error;
  }
};