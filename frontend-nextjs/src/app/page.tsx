'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Users, MessageCircle, Loader2 } from 'lucide-react'

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
}

interface User {
  id: string
  name: string
  status: 'online' | 'offline'
  preferences: {
    dietary_restrictions: string[]
    cuisines: string[]
    music_genres: string[]
    budget: string
    profession?: string
  }
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: '👋 Hi! I\'m your Akin AI assistant. Try asking me to plan something with Bob, Alice, Charlie, or Diana!',
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const users: User[] = [
    {
      id: 'demo-user',
      name: 'Demo User',
      status: 'online',
      preferences: {
        dietary_restrictions: ['pescatarian'],
        cuisines: ['Japanese', 'Thai', 'American'],
        music_genres: ['indie', 'electronic', 'jazz'],
        budget: 'medium'
      }
    },
    {
      id: 'bob-id',
      name: 'Bob',
      status: 'online',
      preferences: {
        dietary_restrictions: ['vegetarian'],
        cuisines: ['Italian', 'Mexican', 'Mediterranean'],
        music_genres: ['rock', 'folk', 'world'],
        budget: 'medium'
      }
    },
    {
      id: 'alice-id',
      name: 'Alice',
      status: 'online',
      preferences: {
        dietary_restrictions: ['none'],
        cuisines: ['French', 'Korean', 'Modern American'],
        music_genres: ['classical', 'ambient', 'experimental'],
        budget: 'high',
        profession: 'Tech Professional'
      }
    },
    {
      id: 'charlie-id',
      name: 'Charlie',
      status: 'online',
      preferences: {
        dietary_restrictions: ['vegan'],
        cuisines: ['Ethiopian', 'Vietnamese', 'Peruvian'],
        music_genres: ['afrobeat', 'reggae', 'hip-hop'],
        budget: 'low',
        profession: 'Creative Artist'
      }
    },
    {
      id: 'diana-id',
      name: 'Diana',
      status: 'online',
      preferences: {
        dietary_restrictions: ['gluten-free', 'dairy-free'],
        cuisines: ['Mediterranean', 'Healthy', 'Salads'],
        music_genres: ['pop', 'dance', 'latin'],
        budget: 'medium',
        profession: 'Fitness Enthusiast'
      }
    }
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:12000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: inputValue,
          user_id: 'demo_user',
          session_id: 'demo_session'
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.reply || 'Sorry, I couldn\'t process that request.',
        isUser: false,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I\'m having trouble connecting. Please make sure the personal agent is running on port 12000.',
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="container mx-auto max-w-7xl px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Akin
          </h1>
          <p className="text-slate-300 text-lg">
            Connect with AI agents to plan experiences with friends
          </p>
        </div>

        {/* Side by Side Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chat Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <MessageCircle size={24} className="text-blue-400" />
              <h2 className="text-2xl font-semibold text-white">Chat</h2>
            </div>
            
            <div className="bg-slate-800/30 backdrop-blur-sm rounded-2xl border border-slate-700 shadow-2xl">
              {/* Messages Container */}
              <div className="h-96 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                        message.isUser
                          ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                          : 'bg-slate-700/50 text-slate-100 border border-slate-600'
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.text}</p>
                      <p className={`text-xs mt-1 ${
                        message.isUser ? 'text-blue-100' : 'text-slate-400'
                      }`}>
                        {message.timestamp.toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-slate-700/50 text-slate-100 border border-slate-600 px-4 py-3 rounded-2xl">
                      <div className="flex items-center gap-2">
                        <Loader2 size={16} className="animate-spin" />
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-slate-700 p-6">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask your Akin network to plan something with your friends..."
                    className="flex-1 bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-xl px-6 py-3 font-medium transition-all shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
                  >
                    <Send size={20} />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Network Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Users size={24} className="text-green-400" />
              <h2 className="text-2xl font-semibold text-white">Network</h2>
            </div>
            
            <div className="grid grid-cols-1 gap-4 max-h-[600px] overflow-y-auto">
              {users.map((user) => (
                <div
                  key={user.id}
                  className="bg-slate-800/30 backdrop-blur-sm rounded-2xl border border-slate-700 p-4 shadow-2xl hover:shadow-blue-500/10 transition-all duration-300"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${
                        user.status === 'online' ? 'bg-green-500' : 'bg-slate-500'
                      }`} />
                      <h3 className="text-lg font-semibold text-white">{user.name}</h3>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm text-slate-400">
                      <span className="font-medium">Status:</span>{' '}
                      <span className={user.status === 'online' ? 'text-green-400' : 'text-slate-400'}>
                        {user.status}
                      </span>
                    </div>

                    {user.preferences.profession && (
                      <div className="text-sm text-slate-400">
                        <span className="font-medium">Role:</span>{' '}
                        <span className="text-slate-300">{user.preferences.profession}</span>
                      </div>
                    )}

                    <div className="text-sm text-slate-400">
                      <span className="font-medium">Dietary:</span>{' '}
                      <span className="text-slate-300">
                        {user.preferences.dietary_restrictions.join(', ')}
                      </span>
                    </div>

                    <div className="text-sm text-slate-400">
                      <span className="font-medium">Cuisines:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {user.preferences.cuisines.map((cuisine) => (
                          <span
                            key={cuisine}
                            className="bg-slate-700/50 text-slate-300 px-2 py-1 rounded-md text-xs"
                          >
                            {cuisine}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="text-sm text-slate-400">
                      <span className="font-medium">Music:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {user.preferences.music_genres.map((genre) => (
                          <span
                            key={genre}
                            className="bg-slate-700/50 text-slate-300 px-2 py-1 rounded-md text-xs"
                          >
                            {genre}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="text-sm text-slate-400">
                      <span className="font-medium">Budget:</span>{' '}
                      <span className="text-slate-300 capitalize">{user.preferences.budget}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
