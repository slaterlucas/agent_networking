import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Clock } from 'lucide-react';
import { apiClient, wsClient, type Message } from '../services/api';

function AgentChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome-alice',
      sender: 'agent',
      agent_name: 'Alice',
      text: "Hi Tiger! I'm Alice, your personal agent. I can help you coordinate your interests and plan dinner with Charlie and Bob. How can I assist you today?",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadMessages();
    setupWebSocket();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      const messagesData = await apiClient.getMessages();
      setMessages(messagesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load messages');
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    wsClient.connect().then(() => {
      wsClient.on('new_message', (data) => {
        if (data.message) {
          setMessages(prev => [...prev, data.message]);
        }
      });

      wsClient.on('chat_broadcast', (data) => {
        // Handle broadcast messages if needed
        console.log('Chat broadcast:', data);
      });
    }).catch(console.error);
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    // Optimistically add the user's message to the chat
    const optimisticMessage: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      agent_name: undefined,
      text: newMessage,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages(prev => [...prev, optimisticMessage]);

    try {
      setSending(true);
      const response = await apiClient.sendMessage({
        message: newMessage,
        agent_id: 'alice' // Default to Alice's agent
      });
      setNewMessage('');
      // Optionally, you could show the agent's reply if the backend returns it
      // But the new endpoint only returns { message: string }
      // If you want to show the agent's reply, you could add it here:
      if (response && response.reply) {
        const agentReply: Message = {
          id: `agent-${Date.now()}`,
          sender: 'agent',
          agent_name: 'Agent',
          text: response.reply,
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages(prev => [
          ...prev,
          agentReply,
        ]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 p-4 mb-4 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Agent Chat
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Communicate with your personal and service agents
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">Online</span>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button 
            onClick={() => setError(null)}
            className="text-xs text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 mt-1"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 px-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-xl ${message.sender === 'user' ? 'order-2' : 'order-1'}`}> {/* wider bubbles */}
              <div className={`flex items-start space-x-2 ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}>
                  {message.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div className={`flex-1 ${message.sender === 'user' ? 'text-right' : ''}`}>
                  {message.agent_name && message.sender === 'agent' && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      {message.agent_name}
                    </p>
                  )}
                  <div className={`inline-block px-0 py-2 rounded-none ${
                    message.sender === 'user'
                      ? 'bg-transparent text-blue-600 font-medium'
                      : 'bg-transparent text-gray-900 dark:text-white'
                  }`}>
                    <p className="text-base whitespace-pre-line">{message.text}</p>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center ${message.sender === 'user' ? 'justify-end' : ''}">
                    <Clock className="w-3 h-3 mr-1" />
                    {message.timestamp}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
        <div className="flex space-x-4">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Start typing or upload a file..."
            className="flex-1 bg-transparent outline-none text-base placeholder-gray-400 dark:placeholder-gray-500"
            disabled={sending}
            style={{ border: 'none', boxShadow: 'none' }}
          />
          <button
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || sending}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {sending ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AgentChat; 