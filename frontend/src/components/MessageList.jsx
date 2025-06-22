import React from 'react';
import './MessageList.css';

const MessageList = ({ messages }) => {
  return (
    <div className="message-list">
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.role}`}>
          <div className="message-content">
            {msg.content}
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;