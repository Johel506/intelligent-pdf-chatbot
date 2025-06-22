// frontend/src/components/ChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { sendMessage } from '../services/api'; // Import our new API function
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState('session-' + Date.now()); // Generate a unique session ID
  const [isLoading, setIsLoading] = useState(false); // To show a loading indicator

  const handleSendMessage = async () => {
    if (input.trim() === '' || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');
    setIsLoading(true);

    // Call the real backend API
    const aiResponseContent = await sendMessage(input, conversationId);

    const aiMessage = { role: 'ai', content: aiResponseContent };
    setMessages(prevMessages => [...prevMessages, aiMessage]);
    setIsLoading(false);
  };

  const handleReset = () => {
    setMessages([]);
    // Generate a new conversation ID for the new session
    setConversationId('session-' + Date.now());
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>PDF Chatbot</h2>
        <button className="reset-button" onClick={handleReset}>Reset</button>
      </div>
      <MessageList messages={messages} />
      {/* We add a simple loading indicator */}
      {isLoading && <div className="loading-indicator">AI is thinking...</div>}
      <MessageInput 
        input={input}
        setInput={setInput}
        handleSendMessage={handleSendMessage}
      />
    </div>
  );
};

export default ChatInterface;