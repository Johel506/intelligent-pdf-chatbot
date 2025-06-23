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
    const scrollHeight = e.target.scrollHeight;
    const maxHeight = 150; // Should match max-height in CSS
    e.target.style.height = Math.min(scrollHeight, maxHeight) + 'px';
  };

  return (
    <div className="message-input-container">
      <textarea
        className="message-input"
        placeholder={disabled ? "Waiting for AI response..." : "Ask me anything..."}
        value={input}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        rows="1"
      />
      <button 
        className={`send-button ${disabled ? 'loading' : ''}`} 
        onClick={handleSendMessage} 
        disabled={disabled || input.trim() === ''}
        aria-label="Send message"
      >
        {/* Replace the text 'Send' with an icon */}
        ➤
      </button>
    </div>
  );
};

export default MessageInput;