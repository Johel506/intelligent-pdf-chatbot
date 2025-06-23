// frontend/src/components/ChatInterface.jsx
import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState('session-' + Date.now());
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (input.trim() === '' || isLoading) return;

    const userMessage = { role: 'user', content: input };
    // Add user message and an empty placeholder for the AI's response
    setMessages(prev => [...prev, userMessage, { role: 'ai', content: '' }]);
    
    const messageToSend = input;
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          setIsLoading(false);
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Process each complete line
        let lines = buffer.split('\n');
        buffer = lines.pop(); // The last line may be incomplete

        for (let line of lines) {
          line = line.trim();
          if (!line) continue;
          // If your backend sends 'data: {...}', remove the prefix:
          if (line.startsWith('data: ')) line = line.slice(6);
          try {
            const data = JSON.parse(line);
            // --- DIAGNOSTIC LOG ---
            console.log('Received stream data:', data); 

            if (data.type === 'content') {
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                lastMessage.content += data.content;
                return newMessages;
              });
            } else if (data.type === 'done') {
              setIsLoading(false);
              return;
            }
          } catch (e) {
            console.error("Failed to parse stream data chunk:", line);
          }
        }
        // At the end, you could try to parse what remains in buffer if it's not empty
      }
    } catch (err) {
      console.error("Failed to fetch stream:", err);
      // Update the last message with an error
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].content = 'Error: Could not connect to the service.';
        return newMessages;
      });
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([]);
    setConversationId('session-' + Date.now());
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>PDF Chatbot</h2>
        <button className="reset-button" onClick={handleReset}>Reset</button>
      </div>
      <MessageList messages={messages} />
      {isLoading && (
        <div className="loading-indicator">
          <span>AI is typing</span>
          <div className="typing-dots">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
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