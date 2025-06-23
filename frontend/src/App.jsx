import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import ConversationSidebar from './components/ConversationSidebar';
import './App.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  // Effect to create a default conversation on first load
  useEffect(() => {
    if (conversations.length === 0) {
      handleNewChat();
    }
    // eslint-disable-next-line
  }, []);

  const handleNewChat = () => {
    const nextNumber = conversations.length + 1;
    const newConversation = {
      id: 'session-' + Date.now(),
      name: `Chat ${nextNumber}`,
      messages: [],
      isPinned: false,
    };
    setConversations(prev => [...prev, newConversation]);
    setActiveConversationId(newConversation.id);
  };

  const handleSelectConversation = (id) => {
    setActiveConversationId(id);
  };

  // Toggle pin/unpin
  const handleTogglePin = (id) => {
    setConversations(prev =>
      prev.map(conv =>
        conv.id === id ? { ...conv, isPinned: !conv.isPinned } : conv
      )
    );
  };

  // Rename conversation
  const handleRenameConversation = (id, newName) => {
    setConversations(prev =>
      prev.map(conv =>
        conv.id === id ? { ...conv, name: newName } : conv
      )
    );
  };

  // Delete conversation
  const handleDeleteConversation = (id) => {
    setConversations(prev => prev.filter(conv => conv.id !== id));
    if (activeConversationId === id) {
      // If the deleted conversation was active, select another
      const remaining = conversations.filter(conv => conv.id !== id);
      setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  // Sort: pinned first, then by creation (id as timestamp)
  const sortedConversations = [...conversations].sort((a, b) => {
    if (a.isPinned === b.isPinned) {
      return parseInt(a.id.replace('session-', '')) - parseInt(b.id.replace('session-', ''));
    }
    return b.isPinned - a.isPinned;
  });

  // Find the currently active conversation object
  const activeConversation = conversations.find(c => c.id === activeConversationId);

  const handleSetMessages = (newMessages) => {
    setConversations(prev => 
      prev.map(conv => 
        conv.id === activeConversationId
          ? { ...conv, messages: newMessages }
          : conv
      )
    );
  };

  return (
    <div className="app-container">
      <ConversationSidebar
        conversations={sortedConversations}
        activeConversationId={activeConversationId}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        onTogglePin={handleTogglePin}
        onRenameConversation={handleRenameConversation}
        onDeleteConversation={handleDeleteConversation}
      />
      {activeConversation ? (
        <ChatInterface
          key={activeConversation.id} // Important for React to re-mount the component
          conversation={activeConversation}
          setMessages={handleSetMessages}
        />
      ) : (
        <div className="no-chat-selected">
          <h2>Welcome</h2>
          <p>Select a conversation or start a new one.</p>
        </div>
      )}
    </div>
  );
}

export default App;