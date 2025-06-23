import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MessageList.css';

const MessageList = ({ messages }) => {
  const listEndRef = useRef(null);

  // This hook will scroll to the bottom every time a new message is added
  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const getAvatar = (role) => {
    if (role === 'user') {
      return (
        <div className="avatar user-avatar">
          <span>👤</span>
        </div>
      );
    } else {
      return (
        <div className="avatar ai-avatar">
          <span>🤖</span>
        </div>
      );
    }
  };

  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="empty-chat-container">
          <div className="empty-chat-logo">🤖</div>
          <h2>Welcome to PDF Chatbot</h2>
          <p>
            I'm ready to help you with your document.
            <br />
            Start by typing your question below.
          </p>
        </div>
      ) : (
        messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.role === 'ai' && getAvatar(msg.role)}
            <div className="message-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            </div>
            {msg.role === 'user' && getAvatar(msg.role)}
          </div>
        ))
      )}
      {/* This empty div is the target for our auto-scroll */}
      <div ref={listEndRef} />
    </div>
  );
};

export default MessageList;