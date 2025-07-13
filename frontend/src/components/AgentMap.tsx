
import { MapPin, Users, MessageSquare, Clock } from 'lucide-react';

interface Location {
  id: string;
  name: string;
  type: 'restaurant' | 'office' | 'event' | 'meeting';
  coordinates: { lat: number; lng: number };
  agents: string[];
  status: 'active' | 'planned' | 'completed';
  description: string;
}

const mockLocations: Location[] = [
  {
    id: '1',
    name: 'Fusion Bistro',
    type: 'restaurant',
    coordinates: { lat: 37.7749, lng: -122.4194 },
    agents: ["Alice's Agent", "Bob's Agent", "Restaurant Finder"],
    status: 'active',
    description: 'Italian-Japanese fusion restaurant'
  },
  {
    id: '2',
    name: 'Tech Startup Office',
    type: 'office',
    coordinates: { lat: 37.7849, lng: -122.4094 },
    agents: ["Charlie's Agent"],
    status: 'planned',
    description: 'Team meeting location'
  },
  {
    id: '3',
    name: 'City Park',
    type: 'event',
    coordinates: { lat: 37.7649, lng: -122.4294 },
    agents: ["Event Coordinator"],
    status: 'active',
    description: 'Outdoor networking event'
  }
];

function AgentMap() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Agent Map
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Visualize agent locations and activities
          </p>
        </div>
        <div className="flex space-x-2">
          <button className="btn-secondary">Filter</button>
          <button className="btn-primary">Add Location</button>
        </div>
      </div>

      {/* Map Placeholder */}
      <div className="card p-6">
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg h-96 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Interactive Map
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Map integration would show agent locations and activities here
            </p>
          </div>
        </div>
      </div>

      {/* Location List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Active Locations
          </h2>
          <div className="space-y-4">
            {mockLocations.filter(loc => loc.status === 'active').map((location) => (
              <div key={location.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <MapPin className="w-4 h-4 text-blue-600" />
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {location.name}
                      </h3>
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                        Active
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {location.description}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                      <div className="flex items-center">
                        <Users className="w-3 h-3 mr-1" />
                        {location.agents.length} agents
                      </div>
                      <div className="flex items-center">
                        <MessageSquare className="w-3 h-3 mr-1" />
                        Collaborating
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Planned Activities
          </h2>
          <div className="space-y-4">
            {mockLocations.filter(loc => loc.status === 'planned').map((location) => (
              <div key={location.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <MapPin className="w-4 h-4 text-purple-600" />
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {location.name}
                      </h3>
                      <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full">
                        Planned
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {location.description}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                      <div className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        Tomorrow 2:00 PM
                      </div>
                      <div className="flex items-center">
                        <Users className="w-3 h-3 mr-1" />
                        {location.agents.length} agents
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Agent Activity Timeline */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Agent Activities
        </h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <Users className="w-4 h-4 text-blue-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Alice and Bob's agents coordinated lunch at Fusion Bistro
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                2 minutes ago
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
              <MapPin className="w-4 h-4 text-green-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Restaurant Finder discovered 15 new locations
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                5 minutes ago
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
              <Clock className="w-4 h-4 text-purple-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Event Coordinator scheduled team meeting
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                1 hour ago
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgentMap; 