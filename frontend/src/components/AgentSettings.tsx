import { useState } from 'react';
import { User, Shield, Bell, Globe, Database } from 'lucide-react';

interface AgentConfig {
  id: string;
  name: string;
  type: 'personal' | 'service';
  enabled: boolean;
  permissions: string[];
  lastUpdated: string;
}

const mockAgentConfigs: AgentConfig[] = [
  {
    id: '1',
    name: "Alice's Personal Agent",
    type: 'personal',
    enabled: true,
    permissions: ['location', 'calendar', 'preferences', 'communication'],
    lastUpdated: '2 minutes ago'
  },
  {
    id: '2',
    name: 'Restaurant Finder',
    type: 'service',
    enabled: true,
    permissions: ['search', 'location', 'recommendations'],
    lastUpdated: '1 hour ago'
  },
  {
    id: '3',
    name: 'Event Coordinator',
    type: 'service',
    enabled: false,
    permissions: ['calendar', 'scheduling'],
    lastUpdated: '3 days ago'
  }
];

function AgentSettings() {
  const [activeTab, setActiveTab] = useState('agents');
  const [agentConfigs, setAgentConfigs] = useState<AgentConfig[]>(mockAgentConfigs);

  const toggleAgent = (id: string) => {
    setAgentConfigs(prev => 
      prev.map(agent => 
        agent.id === id ? { ...agent, enabled: !agent.enabled } : agent
      )
    );
  };

  const tabs = [
    { id: 'agents', label: 'Agents', icon: User },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'integrations', label: 'Integrations', icon: Globe },
    { id: 'data', label: 'Data', icon: Database }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Agent Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Configure your agents and manage preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  isActive
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'agents' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Agent Management
              </h2>
              <button className="btn-primary">Add New Agent</button>
            </div>
            
            <div className="space-y-4">
              {agentConfigs.map((agent) => (
                <div key={agent.id} className="card p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                        <User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          {agent.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {agent.type} • Last updated {agent.lastUpdated}
                        </p>
                        <div className="flex items-center space-x-2 mt-2">
                          {agent.permissions.map((permission) => (
                            <span
                              key={permission}
                              className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full"
                            >
                              {permission}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={agent.enabled}
                          onChange={() => toggleAgent(agent.id)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                          Enabled
                        </span>
                      </label>
                      <button className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
                        Configure
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Privacy Settings
            </h2>
            
            <div className="card p-6">
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Data Sharing
              </h3>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Allow agents to share location data for coordination
                  </span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Share calendar availability with other agents
                  </span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Allow agents to access personal preferences
                  </span>
                </label>
              </div>
            </div>

            <div className="card p-6">
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Communication Preferences
              </h3>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Receive notifications about agent collaborations
                  </span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Allow agents to send direct messages
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Notification Settings
            </h2>
            
            <div className="card p-6">
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Agent Activities
              </h3>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Agent collaboration updates
                  </span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Location-based recommendations
                  </span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                  <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                    Agent performance reports
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'integrations' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Integrations
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card p-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                    <Globe className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">Exa API</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Web search integration</p>
                  </div>
                  <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                    Connected
                  </span>
                </div>
              </div>

              <div className="card p-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                    <Database className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">A2A Registry</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Agent discovery service</p>
                  </div>
                  <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                    Connected
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'data' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Data Management
            </h2>
            
            <div className="card p-6">
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Data Export
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Download your agent data and preferences
              </p>
              <button className="btn-secondary">Export Data</button>
            </div>

            <div className="card p-6">
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Clear Data
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Remove all agent data and reset preferences
              </p>
              <button className="btn-secondary text-red-600 hover:text-red-700 dark:text-red-400">
                Clear All Data
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AgentSettings; 