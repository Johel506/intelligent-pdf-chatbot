// frontend/src/components/MessageInput.jsx
import React from 'react';
import './MessageInput.css';

// We receive props from the parent component (ChatInterface)
const MessageInput = ({ input, setInput, handleSendMessage }) => {
  
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="message-input-container">
      <input
        type="text"
        className="message-input"
        placeholder="Type your message..."
        value={input} // The value is controlled by the parent's state
        onChange={(e) => setInput(e.target.value)} // The parent's function updates the state
        onKeyDown={handleKeyDown} // Allows sending with the Enter key
      />
      <button className="send-button" onClick={handleSendMessage}>
        Send
      </button>
    </div>
  );
};

export default MessageInput;