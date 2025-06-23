// frontend/src/components/ConversationSidebar.jsx

import React, { useState, useRef, useEffect } from 'react';
import './ConversationSidebar.css';

// The ConversationItem component does not need changes, your version is correct.
function ConversationItem({ conversation, isActive, onSelect, onTogglePin, onRename, onDelete, isDeletable }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(conversation.name);
  const menuRef = useRef(null);
  const inputRef = useRef(null);

  // Close menu on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [menuOpen]);

  // Focus input when renaming
  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editing]);

  const handleRename = () => {
    if (editValue.trim() && editValue !== conversation.name) {
      onRename(conversation.id, editValue.trim());
    }
    setEditing(false);
  };

  return (
    <div
      className={`conversation-item${isActive ? ' active' : ''}`}
      onClick={() => !editing && onSelect(conversation.id)}
      tabIndex={0}
    >
      <span className="conversation-name">
        {conversation.isPinned && <span className="pin-icon" title="Pinned">📌</span>}
        {editing ? (
          <input
            ref={inputRef}
            className="rename-input"
            value={editValue}
            onChange={e => setEditValue(e.target.value)}
            onBlur={handleRename}
            onKeyDown={e => {
              if (e.key === 'Enter') handleRename();
              if (e.key === 'Escape') setEditing(false);
            }}
          />
        ) : (
          <span>{conversation.name || 'New Conversation'}</span>
        )}
      </span>
      <span
        className="kebab-menu-icon"
        onClick={e => {
          e.stopPropagation();
          setMenuOpen(v => !v);
        }}
        tabIndex={0}
        onKeyDown={e => { if (e.key === 'Enter') setMenuOpen(v => !v); }}
      >
        &#8942;
      </span>
      {menuOpen && (
        <div className="context-menu" ref={menuRef} onClick={e => e.stopPropagation()}>
          <button className="context-menu-item" onClick={() => { onTogglePin(conversation.id); setMenuOpen(false); }}>
            {conversation.isPinned ? 'Unpin' : 'Pin'}
          </button>
          <button className="context-menu-item" onClick={() => { setEditing(true); setMenuOpen(false); }}>
            Rename
          </button>
          {isDeletable && (
            <button
              className="context-menu-item delete"
              onClick={() => {
                setMenuOpen(false);
                onDelete(conversation.id);
              }}
            >
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// --- MAIN COMPONENT WITH THE CORRECT STRUCTURE ---
const ConversationSidebar = ({
  conversations,
  activeConversationId,
  onNewChat,
  onSelectConversation,
  onTogglePin,
  onRenameConversation,
  onDeleteConversation,
  onToggleSidebar,
  isNewChatDisabled
}) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        {/* This container aligns the title and the close button */}
        <div className="sidebar-title-container">
          <h3>Conversations</h3>
          <button className="sidebar-close-button" onClick={onToggleSidebar}>
            &times;
          </button>
        </div>
        
        {/* The new chat button goes next, on its own line */}
        <button 
          className="new-chat-button" 
          onClick={onNewChat}
          disabled={isNewChatDisabled}
        >
          + New Chat
        </button>
      </div>

      <div className="conversation-list">
        {conversations.map((conv) => (
          <ConversationItem
            key={conv.id}
            conversation={conv}
            isActive={conv.id === activeConversationId}
            onSelect={onSelectConversation}
            onTogglePin={onTogglePin}
            onRename={onRenameConversation}
            onDelete={onDeleteConversation}
            isDeletable={conversations.length > 1}
          />
        ))}
      </div>
    </div>
  );
};

export default ConversationSidebar;