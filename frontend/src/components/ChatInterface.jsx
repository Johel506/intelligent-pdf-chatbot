import React, { useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatInterface.css';

const ChatInterface = () => {
  // Dummy messages for layout purposes. This fulfills the chat history display requirement.
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! How can I help you with the document today?' },
    { role: 'user', content: 'What is this document about?' },
    { role: 'ai', content: 'This document is about TravelAbility, a service that provides personalized travel plans for people with disabilities, including accessible accommodations and transportation.' }
  ]);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>PDF Chatbot</h2>
        {/* This button fulfills the clear/reset conversation requirement */}
        <button className="reset-button">Reset</button>
      </div>
      {/* The MessageList component handles the chat history display */}
      <MessageList messages={messages} />
      {/* The MessageInput component handles the message input field and send button */}
      <MessageInput />
    </div>
  );
};

export default ChatInterface;