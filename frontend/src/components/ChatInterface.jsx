// frontend/src/components/ChatInterface.jsx
import React, { useState, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatInterface.css';
import exportIcon from '../assets/export-icon.svg';
import { t } from '../utils/translations';

const ChatInterface = ({ conversation, setMessages, onToggleSidebar }) => {
  const { id: conversationId, messages } = conversation;
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const abortControllerRef = useRef(null);

  // Export conversation as Markdown
  const handleExportConversation = () => {
    const formattedContent = conversation.messages.map(msg => {
      const prefix = msg.role === 'user' ? '**You:**' : '**AI:**';
      // Remove <sup> tags from content
      const cleanContent = msg.content.replace(/<\/?sup>/g, '');
      return `${prefix}\n${cleanContent}\n\n---\n\n`;
    }).join('');

    const blob = new Blob([formattedContent], { type: 'text/markdown;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${conversation.name.replace(/ /g, '_')}_export.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  };

  const handleSendMessage = async () => {
    const messageToSend = input;
    if (messageToSend.trim() === '' || isLoading) return;

    const userMessage = { role: 'user', content: messageToSend };
    const aiPlaceholder = { role: 'ai', content: '', sources: [] };
    const initialMessages = [...messages, userMessage, aiPlaceholder];
    
    setMessages(initialMessages);
    setInput('');
    setIsLoading(true);
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend,
          conversation_id: conversationId,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        let errorKey = 'serverError';
        if (response.status === 429) {
          errorKey = 'rateLimitError';
        }
        
        const messagesOnError = initialMessages.slice(0, -1);
        const errorMsg = { role: 'ai', content: t(errorKey), sources: [] };
        setMessages([...messagesOnError, errorMsg]);
        
        setIsLoading(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentMessages = [...initialMessages];

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          setIsLoading(false);
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n');
        buffer = lines.pop();

        for (let line of lines) {
          if (!line.trim().startsWith('data:')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            const lastMessage = currentMessages[currentMessages.length - 1];
            
            if (data.type === 'sources') {
              lastMessage.sources = data.sources;
            } else if (data.type === 'content') {
              lastMessage.content += data.content;
            }
            
            setMessages([...currentMessages]);

          } catch (e) {
            console.error("Failed to parse stream data chunk:", line, e);
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Fetch aborted.');
        return;
      }
      
      console.error("Network error:", err);
      
      const messagesOnError = initialMessages.slice(0, -1);
      const errorMsg = { role: 'ai', content: t('networkError'), sources: [] };
      setMessages([...messagesOnError, errorMsg]);
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    // Reset is now simply clearing the messages of the current conversation
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setMessages([]);
    setInput('');
    setIsLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="hamburger-menu" onClick={onToggleSidebar}>
          ☰
        </button>
        <h2>{conversation.name || 'PDF Chatbot'}</h2>
        <div className="header-buttons">
          {/* Export button */}
          <button className="header-button export-button" onClick={handleExportConversation} title="Export Conversation">
            <span>Export</span>
            <img src={exportIcon} alt="Export" className="export-icon" />           
          </button>
          {/* Clear Chat button */}
          <button className="header-button reset-button" onClick={handleReset}>
            Clear Chat
          </button>
        </div>
      </div>
      <MessageList messages={messages} />
      {isLoading && (
        <div className="loading-indicator">
          <span>AI is typing</span>
          <div className="typing-dots"></div>
        </div>
      )}
      <MessageInput 
        input={input}
        setInput={setInput}
        handleSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  );
};

export default ChatInterface;