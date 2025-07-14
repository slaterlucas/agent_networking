'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Users, MessageCircle, Loader2 } from 'lucide-react'
import Link from 'next/link'

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
      text: '👋 Hi! I\'m your Akin AI assistant. Try asking me to plan something with Bob, Tiger, Charlie, or Diana!',
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSearchModal, setShowSearchModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
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
      id: 'tiger-id',
      name: 'Tiger',
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
          session_id: 'curl_test'
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

  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      // Mock search functionality
      alert(`🔍 Searching for profiles matching "${searchQuery || 'all criteria'}"... Found 12 similar profiles! This feature is coming soon.`);
      setShowSearchModal(false);
      setSearchQuery('');
    }
  }

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setShowSearchModal(false);
      }
    }

    if (showSearchModal) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [showSearchModal])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 via-indigo-950 to-slate-950 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-cyan-500/5"></div>
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
      
      <div className="relative z-10 container mx-auto max-w-7xl px-4 py-8">
        {/* Header */}
        <div className="flex justify-center mb-12">
          <div className="relative bg-slate-800/20 backdrop-blur-xl rounded-3xl border border-slate-700/50 shadow-2xl shadow-slate-900/50 px-12 py-8 max-w-2xl overflow-hidden">
            {/* Glass effect overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-white/5 to-transparent"></div>
            
            {/* Decorative elements */}
            <div className="absolute top-2 right-2 w-8 h-8 bg-blue-500/20 rounded-full blur-xl"></div>
            <div className="absolute bottom-2 left-2 w-6 h-6 bg-purple-500/20 rounded-full blur-xl"></div>
            
            <div className="relative text-center">
              <div className="mb-4">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-blue-100 to-cyan-100 bg-clip-text text-transparent mb-2">
                  Akin
                </h1>
                <div className="h-0.5 w-16 bg-gradient-to-r from-blue-500 to-cyan-500 mx-auto rounded-full shadow-lg shadow-blue-500/50"></div>
              </div>
              <p className="text-slate-300 text-lg leading-relaxed">
                Connect with AI agents to plan experiences with friends
              </p>
            </div>
          </div>
        </div>

        {/* Side by Side Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Chat Section */}
          <div className="lg:col-span-3 space-y-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl shadow-lg">
                <MessageCircle size={24} className="text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white">Chat</h2>
            </div>
            
            <div className="bg-slate-800/20 backdrop-blur-xl rounded-3xl border border-slate-700/50 shadow-2xl shadow-slate-900/50 relative overflow-hidden">
              {/* Glass effect overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-white/2 to-transparent"></div>
              
              {/* Messages Container */}
              <div className="relative h-[600px] overflow-y-auto p-8 space-y-6">
                                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-lg px-6 py-4 rounded-2xl relative ${
                          message.isUser
                            ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-2xl shadow-blue-500/30'
                            : 'bg-slate-700/40 backdrop-blur-md text-slate-100 border border-slate-600/50 shadow-xl shadow-slate-900/30'
                        }`}
                      >
                        <p className="text-sm leading-relaxed">{message.text}</p>
                        <p className={`text-xs mt-2 ${
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
                    <div className="bg-slate-700/40 backdrop-blur-md text-slate-100 border border-slate-600/50 px-6 py-4 rounded-2xl shadow-xl shadow-slate-900/30">
                      <div className="flex items-center gap-3">
                        <Loader2 size={18} className="animate-spin text-blue-400" />
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="relative border-t border-slate-700/50 p-8">
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask your Akin network to plan something with your friends..."
                    className="flex-1 bg-slate-700/30 backdrop-blur-md border border-slate-600/50 rounded-2xl px-6 py-4 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 shadow-inner transition-all duration-200"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white rounded-2xl px-8 py-4 font-medium transition-all duration-200 shadow-2xl shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105"
                  >
                    <Send size={20} />
                  </button>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="p-6">
                <div className="flex justify-center gap-4">
                  <Link href="/preferences">
                    <button className="group relative bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white font-semibold py-4 px-8 rounded-2xl shadow-2xl shadow-emerald-500/30 hover:shadow-emerald-500/50 transition-all duration-300 hover:scale-105 overflow-hidden">
                      {/* Glass effect overlay */}
                      <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-white/5 to-transparent"></div>
                      
                      {/* Animated background effect */}
                      <div className="absolute inset-0 bg-gradient-to-r from-emerald-400/20 to-blue-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      
                      <div className="relative flex items-center gap-3">
                        <svg className="w-5 h-5 group-hover:rotate-180 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        <span>Update Preferences</span>
                        <div className="w-2 h-2 bg-white/50 rounded-full group-hover:bg-white/80 transition-colors duration-300"></div>
                      </div>
                      
                      {/* Ripple effect on hover */}
                      <div className="absolute inset-0 bg-white/10 rounded-2xl scale-0 group-hover:scale-100 transition-transform duration-300 opacity-0 group-hover:opacity-100"></div>
                    </button>
                  </Link>
                  
                  <button
                    onClick={() => {
                      // Open Google Calendar in a new tab
                      window.open('https://calendar.google.com', '_blank');
                    }}
                    className="group relative bg-gradient-to-r from-orange-600 to-yellow-600 hover:from-orange-700 hover:to-yellow-700 text-white font-semibold py-4 px-8 rounded-2xl shadow-2xl shadow-orange-500/30 hover:shadow-orange-500/50 transition-all duration-300 hover:scale-105 overflow-hidden"
                  >
                    {/* Glass effect overlay */}
                    <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-white/5 to-transparent"></div>
                    
                    {/* Animated background effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-orange-400/20 to-yellow-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    
                    <div className="relative flex items-center gap-3">
                      <svg className="w-5 h-5 group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>Calendar Integration</span>
                      <div className="w-2 h-2 bg-white/50 rounded-full group-hover:bg-white/80 transition-colors duration-300"></div>
                    </div>
                    
                    {/* Ripple effect on hover */}
                    <div className="absolute inset-0 bg-white/10 rounded-2xl scale-0 group-hover:scale-100 transition-transform duration-300 opacity-0 group-hover:opacity-100"></div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Network Section */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-xl shadow-lg">
                <Users size={24} className="text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white">Network</h2>
            </div>
            
            <div className="grid grid-cols-1 gap-6 max-h-[700px] overflow-y-auto pr-2">
              {users.map((user) => (
                <div
                  key={user.id}
                  className="bg-slate-800/20 backdrop-blur-xl rounded-3xl border border-slate-700/50 p-6 shadow-2xl shadow-slate-900/50 hover:shadow-blue-500/20 transition-all duration-300 hover:scale-105 relative overflow-hidden"
                >
                  {/* Glass effect overlay */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-white/2 to-transparent"></div>
                  
                  <div className="relative">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-4 h-4 rounded-full shadow-lg ${
                          user.status === 'online' ? 'bg-green-500 shadow-green-500/50' : 'bg-slate-500 shadow-slate-500/50'
                        }`} />
                        <h3 className="text-xl font-bold text-white">{user.name}</h3>
                      </div>
                    </div>

                    <div className="space-y-3">
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
                            className="bg-slate-700/40 backdrop-blur-sm text-slate-300 px-3 py-1 rounded-lg text-xs shadow-md"
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
                              className="bg-slate-700/40 backdrop-blur-sm text-slate-300 px-3 py-1 rounded-lg text-xs shadow-md"
                            >
                              {genre}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Find Similar Profiles Button */}
            <div className="mt-8 flex justify-center">
                              <button
                  onClick={() => {
                    setShowSearchModal(true);
                  }}
                className="group relative bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-4 px-8 rounded-2xl shadow-2xl shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105 overflow-hidden"
              >
                {/* Glass effect overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-white/5 to-transparent"></div>
                
                {/* Animated background effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                <div className="relative flex items-center gap-3">
                  <svg className="w-5 h-5 group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Find Similar Profiles</span>
                  <div className="w-2 h-2 bg-white/50 rounded-full group-hover:bg-white/80 transition-colors duration-300"></div>
                </div>
                
                {/* Ripple effect on hover */}
                <div className="absolute inset-0 bg-white/10 rounded-2xl scale-0 group-hover:scale-100 transition-transform duration-300 opacity-0 group-hover:opacity-100"></div>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Search Modal Overlay */}
      {showSearchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-slate-900/60 backdrop-blur-md"
            onClick={() => setShowSearchModal(false)}
          ></div>
          
          {/* Modal Content */}
          <div className="relative z-10 w-full max-w-2xl mx-4">
            <div className="bg-slate-800/30 backdrop-blur-xl rounded-3xl border border-slate-700/50 shadow-2xl shadow-slate-900/50 p-8 relative overflow-hidden">
              {/* Glass effect overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-white/5 to-transparent"></div>
              
              {/* Decorative elements */}
              <div className="absolute top-2 right-2 w-8 h-8 bg-purple-500/20 rounded-full blur-xl"></div>
              <div className="absolute bottom-2 left-2 w-6 h-6 bg-pink-500/20 rounded-full blur-xl"></div>
              
              <div className="relative">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl shadow-lg">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <h2 className="text-2xl font-bold text-white">Find Similar Profiles</h2>
                  </div>
                  <button
                    onClick={() => setShowSearchModal(false)}
                    className="p-2 hover:bg-slate-700/50 rounded-xl transition-colors"
                  >
                    <svg className="w-6 h-6 text-slate-400 hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* Search Input */}
                <div className="mb-6">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={handleSearchKeyPress}
                      placeholder="Search by interests, location, profession..."
                      className="w-full bg-slate-700/30 backdrop-blur-md border border-slate-600/50 rounded-2xl pl-12 pr-4 py-4 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 shadow-inner transition-all duration-200"
                      autoFocus
                    />
                  </div>
                </div>

                {/* Search Suggestions */}
                <div className="space-y-3 mb-6">
                  <p className="text-slate-300 text-sm font-medium">Popular searches:</p>
                  <div className="flex flex-wrap gap-2">
                    {['Tech professionals', 'Food enthusiasts', 'Music lovers', 'Outdoor adventurers', 'Art & culture'].map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => setSearchQuery(suggestion)}
                        className="px-4 py-2 bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-xl text-slate-300 hover:text-white hover:bg-slate-600/40 transition-all duration-200 text-sm"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Search Button */}
                <div className="flex justify-center">
                  <button
                    onClick={() => {
                      // Mock search functionality
                      alert(`🔍 Searching for profiles matching "${searchQuery || 'all criteria'}"... Found 12 similar profiles! This feature is coming soon.`);
                      setShowSearchModal(false);
                      setSearchQuery('');
                    }}
                    className="group relative bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-3 px-8 rounded-2xl shadow-2xl shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105 overflow-hidden"
                  >
                    {/* Glass effect overlay */}
                    <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-white/5 to-transparent"></div>
                    
                    <div className="relative flex items-center gap-3">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span>Search Profiles</span>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
