# Agent Networking API Documentation

This document describes the REST API endpoints for the Agent Networking system, including the main backend API and the dedicated networking API.

## Overview

The system consists of multiple services:
- **Main Backend API** (port 8000): Main application API with agent communication
- **Networking API** (port 8001): Dedicated networking and clustering functionality
- **Agent Servers** (ports 10003-10005): Individual A2A agents

## Main Backend API (Port 8000)

### Base URL
```
http://localhost:8000
```

### Core Endpoints

#### GET /
Health check and API information.

**Response:**
```json
{
  "message": "Agent Networking API",
  "version": "1.0.0"
}
```

#### GET /health
Detailed health check including all services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "main_api": "healthy",
    "networking_api": "healthy"
  }
}
```

### Agent Management

#### GET /api/agents
Get all available agents.

**Response:**
```json
[
  {
    "id": "alice",
    "name": "Alice's Agent",
    "type": "personal",
    "status": "online",
    "last_activity": "2 minutes ago",
    "avatar": "A",
    "capabilities": ["search", "networking", "recommendations", "clustering"],
    "location": "San Francisco"
  }
]
```

#### GET /api/agents/{agent_id}
Get specific agent information.

#### GET /api/agents/{agent_id}/status
Get agent status.

### Messaging

#### POST /api/chat
Send a message to an agent.

**Request:**
```json
{
  "message": "Hello, can you help me find similar people?",
  "agent_id": "alice"
}
```

**Response:**
```json
{
  "message": "Message sent successfully",
  "response": "I'll help you find similar people based on your interests..."
}
```

#### GET /api/messages
Get recent chat messages.

**Query Parameters:**
- `limit` (optional): Number of messages to return (default: 50)

### Networking Integration

#### POST /api/networking/similar
Find similar people using the networking system.

**Request:**
```json
{
  "target_person": "Alice",
  "k": 5
}
```

**Response:**
```json
{
  "target_person": "Alice",
  "similar_people": [
    {
      "name": "Bob",
      "similarity": 0.85
    },
    {
      "name": "Charlie", 
      "similarity": 0.72
    }
  ]
}
```

#### POST /api/networking/cluster
Cluster people based on their preferences.

**Request:**
```json
{
  "n_clusters": 3,
  "method": "kmeans"
}
```

**Response:**
```json
{
  "clusters": {
    "Alice": 0,
    "Bob": 1,
    "Charlie": 0
  },
  "cluster_members": {
    "0": ["Alice", "Charlie"],
    "1": ["Bob"],
    "2": ["Diana"]
  },
  "n_clusters": 3,
  "method": "kmeans"
}
```

#### GET /api/networking/clusters/{cluster_id}
Get members of a specific cluster.

**Response:**
```json
{
  "cluster_id": 0,
  "members": ["Alice", "Charlie"]
}
```

#### POST /api/networking/add-person
Add a person to the networking system.

**Request:**
```json
{
  "name": "David",
  "preferences": "I love technology and outdoor activities",
  "interests": ["programming", "hiking"],
  "location": "San Francisco"
}
```

#### GET /api/networking/stats
Get networking system statistics.

**Response:**
```json
{
  "total_people": 10,
  "has_clusters": true,
  "has_similarity_matrix": true,
  "has_feature_matrix": true,
  "n_clusters": 4
}
```

### Other Endpoints

#### GET /api/locations
Get all locations where agents are active.

#### GET /api/activities
Get recent system activities.

#### GET /api/stats
Get system statistics including networking data.

#### GET /api/settings/{agent_id}
Get agent settings.

#### PUT /api/settings/{agent_id}
Update agent settings.

### WebSocket

#### WebSocket /ws
Real-time communication endpoint.

**Message Types:**
- `ping`: Keep connection alive
- `message`: Broadcast message to all clients

## Networking API (Port 8001)

### Base URL
```
http://localhost:8001
```

### Endpoints

#### GET /
API information and available endpoints.

#### POST /networking/similar
Find similar people to a target person.

**Request:**
```json
{
  "target_person": "Alice",
  "k": 5
}
```

#### POST /networking/cluster
Cluster people based on preferences.

**Request:**
```json
{
  "n_clusters": 3,
  "method": "kmeans"
}
```

#### GET /networking/clusters/{cluster_id}
Get cluster members.

#### POST /networking/top-pairs
Find top similar pairs.

**Query Parameters:**
- `k`: Number of pairs to return (default: 10)

#### GET /networking/features
Get important features for clustering.

**Query Parameters:**
- `n_features`: Number of features to return (default: 10)

#### POST /networking/update-preferences
Update people preferences.

**Request:**
```json
{
  "people_preferences": {
    "Alice": "I love technology and programming",
    "Bob": "I enjoy cooking and photography"
  }
}
```

#### GET /networking/people
Get all people in the system.

#### POST /networking/add-person
Add a single person.

**Request:**
```json
{
  "name": "David",
  "preferences": "I love technology and outdoor activities",
  "interests": ["programming", "hiking"],
  "location": "San Francisco"
}
```

#### GET /networking/stats
Get system statistics.

## Agent Servers

### Alice Agent (Port 10003)
- **URL**: `http://localhost:10003`
- **A2A Endpoint**: `http://localhost:10003/a2a/execute`
- **Networking Endpoints**: Available at `/networking/*`

### Bob Agent (Port 10004)
- **URL**: `http://localhost:10004`
- **A2A Endpoint**: `http://localhost:10004/a2a/execute`
- **Networking Endpoints**: Available at `/networking/*`

### Charlie Agent (Port 10005)
- **URL**: `http://localhost:10005`
- **A2A Endpoint**: `http://localhost:10005/a2a/execute`
- **Networking Endpoints**: Available at `/networking/*`

## Usage Examples

### Finding Similar People
```bash
curl -X POST http://localhost:8000/api/networking/similar \
  -H "Content-Type: application/json" \
  -d '{"target_person": "Alice", "k": 3}'
```

### Clustering People
```bash
curl -X POST http://localhost:8000/api/networking/cluster \
  -H "Content-Type: application/json" \
  -d '{"n_clusters": 4, "method": "kmeans"}'
```

### Sending Message to Agent
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find people similar to me", "agent_id": "alice"}'
```

### Getting System Stats
```bash
curl http://localhost:8000/api/stats
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include a detail message:

```json
{
  "detail": "Person 'Unknown' not found in the dataset."
}
```

## WebSocket Events

### Connection
Connect to `ws://localhost:8000/ws`

### Message Events
```json
{
  "type": "message",
  "data": {
    "id": "123",
    "text": "Hello from agent",
    "sender": "agent",
    "timestamp": "10:30 AM",
    "agent_name": "Alice's Agent"
  }
}
```

### Ping/Pong
```json
{"type": "ping"}
```
Response:
```json
{"type": "pong"}
```

## Starting the System

Use the provided script to start all services:

```bash
python3 start_services.py
```

This will start:
1. Networking API (port 8001)
2. Main Backend API (port 8000)
3. Agent servers (ports 10003-10005)
4. Frontend (port 3000)

## Dependencies

Make sure you have the required Python packages installed:

```bash
pip install fastapi uvicorn httpx pydantic python-dotenv
pip install scikit-learn pandas numpy matplotlib seaborn
```

For the frontend:
```bash
cd frontend
npm install
``` 