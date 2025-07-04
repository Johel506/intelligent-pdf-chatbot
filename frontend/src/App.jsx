import React, { useState, useEffect, useRef } from 'react';
import ChatInterface from './components/ChatInterface';
import ConversationSidebar from './components/ConversationSidebar';
import ConfirmationModal from './components/ConfirmationModal';
import './App.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Sidebar open state for mobile
  const [modalState, setModalState] = useState({
    isOpen: false,
    message: '',
    onConfirm: () => {},
    onCancel: () => {}
  });
  const abortControllerRef = useRef(null);

  // Create a default conversation on first load
  useEffect(() => {
    if (conversations.length === 0) {
      handleNewChat();
    }
    // eslint-disable-next-line
  }, []);

  const handleNewChat = () => {
    // --- IMPROVED LOGIC TO FIND THE CORRECT NAME ---
    const existingChatNumbers = conversations
      .map(conv => {
        // Use a regular expression to find the number in "Chat X"
        const match = conv.name.match(/^Chat (\d+)$/);
        return match ? parseInt(match[1], 10) : 0;
      })
      .filter(num => num > 0); // Filter out non-matching

    let nextChatNumber = 1;
    // Find the first number not in use
    while (existingChatNumbers.includes(nextChatNumber)) {
      nextChatNumber++;
    }
    const newName = `Chat ${nextChatNumber}`;
    // --- END IMPROVED LOGIC ---

    const newConversation = {
      id: 'session-' + Date.now(),
      name: newName, // Use the calculated new name
      messages: [],
      isPinned: false, // Make sure to initialize all properties
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

  // Delete conversation after confirmation
  const handleDeleteConversation = (idToDelete) => {
    const remainingConversations = conversations.filter(c => c.id !== idToDelete);
    setConversations(remainingConversations);
    if (activeConversationId === idToDelete) {
      setActiveConversationId(remainingConversations.length > 0 ? remainingConversations[0].id : null);
    }
    setModalState({ isOpen: false }); // Close the modal
  };

  // Open the confirmation modal
  const promptDelete = (id) => {
    setModalState({
      isOpen: true,
      message: 'Delete this conversation permanently?',
      onConfirm: () => handleDeleteConversation(id),
      onCancel: () => setModalState({ isOpen: false })
    });
  };

  // Sort: pinned first, then by creation (id as timestamp)
  const sortedConversations = [...conversations].sort((a, b) => {
    if (a.isPinned === b.isPinned) {
      return parseInt(a.id.replace('session-', '')) - parseInt(b.id.replace('session-', ''));
    }
    return b.isPinned - a.isPinned;
  });

  const activeConversation = conversations.find(c => c.id === activeConversationId);
  const isNewChatDisabled = conversations.some(conv => conv.messages.length === 0);

  // Set messages for the active conversation
  const handleSetMessages = (newMessages) => {
    setConversations(prev => 
      prev.map(conv => 
        conv.id === activeConversationId
          ? { ...conv, messages: newMessages }
          : conv
      )
    );
  };

  // Toggle sidebar open/close (for mobile)
  const handleToggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  return (
    // Add conditional class for sidebar open
    <div className={`app-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      <ConversationSidebar
        conversations={sortedConversations}
        activeConversationId={activeConversationId}
        onNewChat={() => {
          handleNewChat();
          setIsSidebarOpen(false); // Close sidebar when creating new chat
        }}
        onSelectConversation={(id) => {
          handleSelectConversation(id);
          setIsSidebarOpen(false); // Close sidebar on select
        }}
        onTogglePin={handleTogglePin}
        onRenameConversation={handleRenameConversation}
        onDeleteConversation={promptDelete}
        onToggleSidebar={handleToggleSidebar}
        isNewChatDisabled={isNewChatDisabled}
      />
      <div className="sidebar-overlay" onClick={handleToggleSidebar}></div>
      {activeConversation ? (
        <ChatInterface
          key={activeConversation.id}
          conversation={activeConversation}
          setMessages={handleSetMessages}
          onToggleSidebar={handleToggleSidebar}
        />
      ) : (
        <div className="no-chat-selected">
          <button className="hamburger-menu" onClick={handleToggleSidebar}>
            ☰
          </button>
          <h2>Welcome</h2>
          <p>Select a conversation or start a new one.</p>
        </div>
      )}
      <ConfirmationModal
        isOpen={modalState.isOpen}
        message={modalState.message}
        onConfirm={modalState.onConfirm}
        onCancel={modalState.onCancel}
      />
    </div>
  );
}

export default App;