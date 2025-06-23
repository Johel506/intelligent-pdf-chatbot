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
    const newConversation = {
      id: 'session-' + Date.now(),
      name: 'New Conversation',
      messages: [],
    };
    setConversations(prev => [...prev, newConversation]);
    setActiveConversationId(newConversation.id);
  };

  const handleSelectConversation = (id) => {
    setActiveConversationId(id);
  };

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
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
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