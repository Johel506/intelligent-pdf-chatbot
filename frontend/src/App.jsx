import React, { useState, useEffect, useRef } from 'react';
import ChatInterface from './components/ChatInterface';
import ConversationSidebar from './components/ConversationSidebar';
import './App.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Sidebar open state for mobile
  const abortControllerRef = useRef(null);

  // Effect to create a default conversation on first load
  useEffect(() => {
    if (conversations.length === 0) {
      handleNewChat();
    }
    // eslint-disable-next-line
  }, []);

  const handleNewChat = () => {
    // --- LÓGICA MEJORADA PARA ENCONTRAR EL NOMBRE CORRECTO ---
    const existingChatNumbers = conversations
      .map(conv => {
        // Usamos una expresión regular para encontrar el número en "Chat X"
        const match = conv.name.match(/^Chat (\d+)$/);
        return match ? parseInt(match[1], 10) : 0;
      })
      .filter(num => num > 0); // Filtramos los que no coincidan

    let nextChatNumber = 1;
    // Buscamos el primer número que no esté en uso
    while (existingChatNumbers.includes(nextChatNumber)) {
      nextChatNumber++;
    }
    const newName = `Chat ${nextChatNumber}`;
    // --- FIN DE LA LÓGICA MEJORADA ---

    const newConversation = {
      id: 'session-' + Date.now(),
      name: newName, // Usamos el nuevo nombre calculado
      messages: [],
      isPinned: false, // Asegúrate de inicializar todas las propiedades
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

  const activeConversation = conversations.find(c => c.id === activeConversationId);
  const isNewChatDisabled = conversations.some(conv => conv.messages.length === 0);

  // Set messages
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
        onDeleteConversation={handleDeleteConversation}
        onToggleSidebar={handleToggleSidebar}
        isNewChatDisabled={isNewChatDisabled}
      />
      {/* --- Add the sidebar overlay --- */}
      <div className="sidebar-overlay" onClick={handleToggleSidebar}></div>
      {/* --- End overlay --- */}
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
    </div>
  );
}

export default App;