'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, ArrowLeft, Bot, Loader2 } from 'lucide-react'
import Link from 'next/link'

interface InterviewMessage {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
}

export default function PreferencesInterview() {
  const [messages, setMessages] = useState<InterviewMessage[]>([
    {
      id: '1',
      text: '👋 Hello! I\'m your Akin Preferences Agent. I\'ll help you set up your personalized preferences to make your collaborative experiences even better. Let\'s start with some questions!',
      isUser: false,
      timestamp: new Date()
    },
    {
      id: '2',
      text: '🍽️ First, let\'s talk about food. What are your dietary restrictions or preferences? (e.g., vegetarian, vegan, gluten-free, no restrictions)',
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [questionIndex, setQuestionIndex] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const interviewQuestions = [
    "🍽️ Great! Now, what types of cuisines do you enjoy? (e.g., Italian, Japanese, Mexican, Mediterranean)",
    "🎵 What music genres do you like? This helps us suggest concerts and events. (e.g., rock, jazz, electronic, classical)",
    "🎯 What activities do you enjoy in your free time? (e.g., hiking, museums, sports, arts & crafts)",
    "🌍 Do you prefer indoor or outdoor activities, or a mix of both?",
    "💰 What's your typical budget range for social activities? (low, medium, high)",
    "⏰ What time of day do you prefer for social activities? (morning, afternoon, evening, flexible)",
    "✨ Perfect! Your preferences have been saved. You can always come back here to update them. Your Akin network will now provide more personalized recommendations!"
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: InterviewMessage = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Simulate AI processing
    setTimeout(() => {
      if (questionIndex < interviewQuestions.length) {
        const botMessage: InterviewMessage = {
          id: (Date.now() + 1).toString(),
          text: interviewQuestions[questionIndex],
          isUser: false,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, botMessage])
        setQuestionIndex(prev => prev + 1)
      }
      setIsLoading(false)
    }, 1500)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 via-indigo-950 to-slate-950 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-cyan-500/5"></div>
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
      
      <div className="relative z-10 container mx-auto max-w-4xl px-4 py-8 min-h-screen flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link 
            href="/"
            className="p-3 bg-slate-800/30 backdrop-blur-xl rounded-2xl border border-slate-700/50 hover:bg-slate-700/30 transition-colors group"
          >
            <ArrowLeft size={24} className="text-white group-hover:text-blue-400 transition-colors" />
          </Link>
          
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-2xl shadow-lg">
              <Bot size={28} className="text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Preferences Interview</h1>
              <p className="text-slate-300">Personalizing your Akin experience</p>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 bg-slate-800/20 backdrop-blur-xl rounded-3xl border border-slate-700/50 shadow-2xl shadow-slate-900/50 relative overflow-hidden flex flex-col">
          {/* Glass effect overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-white/2 to-transparent"></div>
          
          {/* Messages Container */}
          <div className="relative flex-1 overflow-y-auto p-8 space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-2xl px-6 py-4 rounded-2xl relative ${
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
                    <Loader2 size={18} className="animate-spin text-emerald-400" />
                    <span className="text-sm">Processing your response...</span>
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
                placeholder={questionIndex < interviewQuestions.length ? "Share your preferences..." : "Interview complete! You can return to Akin."}
                className="flex-1 bg-slate-700/30 backdrop-blur-md border border-slate-600/50 rounded-2xl px-6 py-4 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 shadow-inner transition-all duration-200"
                disabled={isLoading || questionIndex >= interviewQuestions.length}
              />
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading || questionIndex >= interviewQuestions.length}
                className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white rounded-2xl px-8 py-4 font-medium transition-all duration-200 shadow-2xl shadow-emerald-500/30 hover:shadow-emerald-500/50 hover:scale-105"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="mt-6 flex justify-center">
          <div className="bg-slate-800/30 backdrop-blur-xl rounded-2xl border border-slate-700/50 px-6 py-3">
            <div className="flex items-center gap-3">
              <span className="text-slate-300 text-sm">Progress:</span>
              <div className="flex gap-1">
                {Array.from({ length: 7 }, (_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      i < questionIndex ? 'bg-emerald-500' : 'bg-slate-600'
                    }`}
                  />
                ))}
              </div>
              <span className="text-slate-300 text-sm">{Math.min(questionIndex, 7)}/7</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 