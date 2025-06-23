import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MessageList.css';

// Utility to extract cited pages from the AI's answer
function extractCitedPages(content) {
  const pageSet = new Set();
  if (!content) return pageSet;
  // Match [Page X] and [Page X, Page Y]
  const inlineMatches = [...content.matchAll(/\[Page ([0-9]+)(?:, Page ([0-9]+))*\]/g)];
  for (const match of inlineMatches) {
    if (match[1]) pageSet.add(Number(match[1]));
    const allPages = match[0].match(/Page ([0-9]+)/g);
    if (allPages) {
      allPages.forEach(p => pageSet.add(Number(p.replace('Page ', ''))));
    }
  }
  // Match final Sources: Page X, Page Y
  const sourcesLine = content.match(/Sources:\s*Page ([0-9]+(?:, Page [0-9]+)*)/);
  if (sourcesLine && sourcesLine[1]) {
    sourcesLine[1].split(',').forEach(p => {
      const num = p.replace('Page ', '').trim();
      if (num) pageSet.add(Number(num));
    });
  }
  return pageSet;
}

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
        messages.map((msg, index) => {
          const citedPages = msg.role === 'ai' ? extractCitedPages(msg.content) : new Set();
          const filteredSources = msg.sources
            ? msg.sources.filter(src => citedPages.has(Number(src.page_number)))
            : [];
          return (
            <div key={index} className={`message ${msg.role}`}>
              {msg.role === 'ai' && getAvatar(msg.role)}
              <div className="message-container">
                <div className="message-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content || "..."}
                  </ReactMarkdown>
                </div>
              </div>
              {msg.role === 'user' && getAvatar(msg.role)}
            </div>
          );
        })
      )}
      {/* This empty div is the target for our auto-scroll */}
      <div ref={listEndRef} />
    </div>
  );
};

export default MessageList;