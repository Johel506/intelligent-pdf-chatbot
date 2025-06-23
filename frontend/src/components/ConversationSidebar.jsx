import React from 'react';
import './ConversationSidebar.css';

const ConversationSidebar = ({ conversations, activeConversationId, onNewChat, onSelectConversation }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>Conversations</h3>
        <button className="new-chat-button" onClick={onNewChat}>
          + New Chat
        </button>
      </div>
      <div className="conversation-list">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
            onClick={() => onSelectConversation(conv.id)}
          >
            <span className="conversation-name">
              {conv.name || 'New Conversation'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversationSidebar; 