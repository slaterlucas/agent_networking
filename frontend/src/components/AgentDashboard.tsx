import React, { useState, useEffect } from 'react';
import { 
  Users, 
  MessageSquare, 
  MapPin, 
  Clock, 
  TrendingUp,
  Activity,
  Plus,
  Settings
} from 'lucide-react';
import { apiClient, wsClient, type Agent, type Activity as ActivityType, type Stats } from '../services/api';

interface Activity {
  id: string;
  type: 'chat' | 'meeting' | 'search' | 'collaboration';
  title: string;
  description: string;
  timestamp: string;
  agentId: string;
}

function AgentDashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activities, setActivities] = useState<ActivityType[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    setupWebSocket();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [agentsData, activitiesData, statsData] = await Promise.all([
        apiClient.getAgents(),
        apiClient.getActivities(),
        apiClient.getStats()
      ]);
      
      setAgents(agentsData);
      setActivities(activitiesData);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    wsClient.connect().then(() => {
      wsClient.on('agent_status_update', (data) => {
        setAgents(prev => 
          prev.map(agent => 
            agent.id === data.agent_id 
              ? { ...agent, status: data.status, last_activity: 'now' }
              : agent
          )
        );
      });

      wsClient.on('new_message', (data) => {
        // Refresh activities when new messages arrive
        loadData();
      });
    }).catch(console.error);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        <button 
          onClick={loadData}
          className="btn-primary"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Agent Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Monitor and manage your personal and service agents
          </p>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Add Agent
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Active Agents
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats?.active_agents || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <MessageSquare className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Conversations
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats?.total_conversations || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <MapPin className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Locations
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats?.total_locations || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Collaborations
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats?.total_collaborations || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Agents */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Active Agents
            </h2>
            <button className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
              View All
            </button>
          </div>
          <div className="space-y-4">
            {agents.map((agent) => (
              <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-400 font-semibold">
                    {agent.avatar}
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {agent.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {agent.type} • {agent.last_activity}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    agent.status === 'online' ? 'bg-green-500' :
                    agent.status === 'busy' ? 'bg-yellow-500' : 'bg-gray-400'
                  }`} />
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {agent.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Recent Activity
            </h2>
            <button className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
              View All
            </button>
          </div>
          <div className="space-y-4">
            {activities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                  {activity.type === 'collaboration' && <Users className="w-4 h-4 text-blue-600" />}
                  {activity.type === 'search' && <MapPin className="w-4 h-4 text-green-600" />}
                  {activity.type === 'meeting' && <Clock className="w-4 h-4 text-purple-600" />}
                  {activity.type === 'chat' && <MessageSquare className="w-4 h-4 text-orange-600" />}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {activity.title}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {activity.description}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    {activity.timestamp}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgentDashboard; 