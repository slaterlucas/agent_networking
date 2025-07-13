import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Users, 
  MessageSquare, 
  Map, 
  Settings, 
  Plus,
  Search,
  Bell,
  User
} from 'lucide-react';
import AgentDashboard from './components/AgentDashboard';
import AgentChat from './components/AgentChat';
import AgentMap from './components/AgentMap';
import AgentSettings from './components/AgentSettings';
import { cn } from './lib/utils';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Users, label: 'Dashboard' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/map', icon: Map, label: 'Map' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Agent Networking
              </h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={cn(
                      'inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200',
                      isActive
                        ? 'border-blue-500 text-gray-900 dark:text-white'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                    )}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
              <Search className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
              <Bell className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
              <User className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navigation />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<AgentDashboard />} />
            <Route path="/chat" element={<AgentChat />} />
            <Route path="/map" element={<AgentMap />} />
            <Route path="/settings" element={<AgentSettings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
