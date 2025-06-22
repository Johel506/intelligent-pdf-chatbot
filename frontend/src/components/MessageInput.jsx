import React from 'react';
import './MessageInput.css';

const MessageInput = ({ input, setInput, handleSendMessage, disabled }) => {
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !disabled) {
      handleSendMessage();
    }
  };

  return (
    <div className="message-input-container">
      <input
        type="text"
        className="message-input"
        placeholder={disabled ? "Waiting for response..." : "Type your message..."}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled} // Disable the input field while loading
      />
      <button className="send-button" onClick={handleSendMessage} disabled={disabled}>
        {disabled ? '...' : 'Send'}
      </button>
    </div>
  );
};

export default MessageInput;