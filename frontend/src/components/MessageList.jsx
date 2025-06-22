import React, { useEffect, useRef } from 'react';
import './MessageList.css';

const MessageList = ({ messages }) => {
  const listEndRef = useRef(null);

  // This hook will scroll to the bottom every time a new message is added
  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="message-list">
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.role}`}>
          <div className="message-content">
            {msg.content}
          </div>
        </div>
      ))}
      {/* This empty div is the target for our auto-scroll */}
      <div ref={listEndRef} />
    </div>
  );
};

export default MessageList;