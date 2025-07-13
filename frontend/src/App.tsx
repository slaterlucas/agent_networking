import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import AgentDashboard from './components/AgentDashboard';
import AgentChat from './components/AgentChat';
import AgentMap from './components/AgentMap';
import AgentSettings from './components/AgentSettings';
import AssistantResults from './components/AssistantResults';
import tigerImg from './assets/Tiger.png';
import akinLogo from './assets/akin-logo.png';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/discover', label: 'Discover' },
    { path: '/assistant', label: 'Assistant' },
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 select-none" style={{ boxShadow: 'none', borderBottom: 'none' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left: Logo */}
          <div className="flex items-center space-x-2">
            <img src={akinLogo} alt="Akin Logo" className="w-8 h-8" />
            <span className="text-lg font-bold tracking-tight text-gray-900 dark:text-white font-sans">Akin</span>
          </div>
          {/* Center: Nav */}
          <div className="flex space-x-8">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`text-base px-2 py-1 font-sans transition-colors duration-200 ${
                    isActive
                      ? 'font-semibold text-gray-900 dark:text-white'
                      : 'font-normal text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
                  }`}
                  style={{ boxShadow: 'none', borderBottom: 'none' }}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
          {/* Right: Profile */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-sans text-gray-700 dark:text-gray-200">Tiger Zhang</span>
            <img
              src={tigerImg}
              alt="Profile"
              className="w-8 h-8 rounded-full border border-gray-200 dark:border-gray-700"
            />
          </div>
        </div>
      </div>
    </nav>
  );
}

function AssistantPage() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-[calc(100vh-8rem)]">
      <div className="overflow-y-auto"><AgentChat /></div>
      <div className="overflow-y-auto"><AssistantResults /></div>
    </div>
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
            <Route path="/discover" element={<AgentMap />} />
            <Route path="/assistant" element={<AssistantPage />} />
            <Route path="/map" element={<AgentMap />} />
            <Route path="/settings" element={<AgentSettings />} />
          </Routes>
      </main>
    </div>
    </Router>
  );
}

export default App;
