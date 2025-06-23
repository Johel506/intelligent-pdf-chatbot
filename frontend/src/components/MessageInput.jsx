import React from 'react';
import './MessageInput.css';

const MessageInput = ({ input, setInput, handleSendMessage, disabled }) => {
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey && !disabled) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  return (
    <div className="message-input-container">
      <textarea
        className="message-input"
        placeholder={disabled ? "Waiting for response..." : "Type your message... (Shift+Enter for new line)"}
        value={input}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        rows="1"
      />
      <button 
        className={`send-button ${disabled ? 'loading' : ''}`} 
        onClick={handleSendMessage} 
        disabled={disabled}
      >
        {disabled ? '...' : 'Send'}
      </button>
    </div>
  );
};

export default MessageInput;