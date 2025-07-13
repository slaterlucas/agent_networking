// API service for communicating with the backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Types
export interface Agent {
  id: string;
  name: string;
  type: 'personal' | 'service';
  status: 'online' | 'offline' | 'busy';
  last_activity: string;
  avatar: string;
  capabilities: string[];
  location?: string;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: string;
  agent_name?: string;
}

export interface Location {
  id: string;
  name: string;
  type: string;
  coordinates: { lat: number; lng: number };
  agents: string[];
  status: string;
  description: string;
}

export interface Activity {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  agents: string[];
}

export interface AgentSettings {
  enabled: boolean;
  permissions: string[];
  privacy_settings: Record<string, boolean>;
  notification_settings: Record<string, boolean>;
}

export interface Stats {
  active_agents: number;
  total_conversations: number;
  total_locations: number;
  total_collaborations: number;
}

export interface ChatRequest {
  message: string;
  agent_id?: string;
}

// API Client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Agents
  async getAgents(): Promise<Agent[]> {
    return this.request<Agent[]>('/api/agents');
  }

  async getAgent(id: string): Promise<Agent> {
    return this.request<Agent>(`/api/agents/${id}`);
  }

  async getAgentStatus(id: string): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/api/agents/${id}/status`);
  }

  // Messages
  async getMessages(limit: number = 50): Promise<Message[]> {
    return this.request<Message[]>(`/api/messages?limit=${limit}`);
  }

  async sendMessage(request: ChatRequest): Promise<{ message: string; response: Message }> {
    return this.request<{ message: string; response: Message }>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Locations
  async getLocations(): Promise<Location[]> {
    return this.request<Location[]>('/api/locations');
  }

  // Activities
  async getActivities(): Promise<Activity[]> {
    return this.request<Activity[]>('/api/activities');
  }

  // Stats
  async getStats(): Promise<Stats> {
    return this.request<Stats>('/api/stats');
  }

  // Settings
  async getAgentSettings(agentId: string): Promise<AgentSettings> {
    return this.request<AgentSettings>(`/api/settings/${agentId}`);
  }

  async updateAgentSettings(agentId: string, settings: AgentSettings): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/settings/${agentId}`, {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; active_connections: number }> {
    return this.request<{ status: string; timestamp: string; active_connections: number }>('/health');
  }
}

// WebSocket Client
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  constructor(private url: string = WS_URL) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  private handleMessage(data: any): void {
    const { type } = data;
    const listeners = this.listeners.get(type) || [];
    listeners.forEach(listener => listener(data));
  }

  on(event: string, callback: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: (data: any) => void): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Create API client instance
export const apiClient = new ApiClient();

// Create WebSocket client instance
export const wsClient = new WebSocketClient();

// Export types
export type { Agent, Message, Location, Activity, AgentSettings, Stats, ChatRequest }; 