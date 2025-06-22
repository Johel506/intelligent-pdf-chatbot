import React from 'react';
import './MessageInput.css';

const MessageInput = () => {
  return (
    <div className="message-input-container">
      <input
        type="text"
        className="message-input"
        placeholder="Type your message..."
      />
      <button className="send-button">Send</button>
    </div>
  );
};

export default MessageInput;