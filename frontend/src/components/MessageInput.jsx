import React, { useRef, useEffect } from 'react';
import './MessageInput.css';

const MessageInput = ({ input, setInput, handleSendMessage, disabled }) => {
  const textareaRef = useRef(null);

  const resizeTextarea = () => {
    if (textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'auto'; // Reset height to recalculate
      const newHeight = Math.min(textarea.scrollHeight, 120); // Max height 120px
      textarea.style.height = `${newHeight}px`;
    }
  };

  // Resize on input change
  useEffect(() => {
    resizeTextarea();
  }, [input]);

  // Resize after AI response is finished
  useEffect(() => {
    // We only want to trigger this when loading is finished, not when it starts.
    if (!disabled) {
      resizeTextarea();
    }
  }, [disabled]);

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey && !disabled) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  return (
    <div className="message-input-container">
      <textarea
        ref={textareaRef}
        className="message-input"
        placeholder={disabled ? "Waiting for response..." : "Type your message..."}
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