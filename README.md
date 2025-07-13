# Agent Networking: Collaborative Personal Agents

## 🎯 Project Vision

**Agent Networking** is a revolutionary approach to personal AI assistance where each individual has their own personalized agent that understands their preferences, habits, and needs. These personal agents can then collaborate with each other and specialized service agents to solve complex, multi-person coordination tasks.

### The Core Concept

Imagine a world where:
- **You have your own personal AI agent** that knows your food preferences, schedule, location, budget, and dietary restrictions
- **Your friend has their own personal AI agent** with their own unique preferences and constraints
- **When you want to meet for lunch**, your agents can collaborate to find the perfect restaurant that satisfies both of your preferences
- **Specialized agents** (like our restaurant finder) provide domain expertise to help make the best decisions

### Example Use Case: Collaborative Lunch Planning

```
Person A's Agent: "My human wants to meet Person B for lunch. 
I know they prefer Italian food, are vegetarian, have a $30 budget, 
and are available between 12-2pm today."

Person B's Agent: "My human is available 1-3pm, loves sushi, 
has a $50 budget, and prefers quiet restaurants for business meetings."

Restaurant Finder Agent: "Based on both preferences, I found 
'Fusion Bistro' - it has both Italian and Japanese options, 
quiet atmosphere, vegetarian choices, and fits both budgets. 
It's located at 123 Main St, 15 minutes from both locations."

Both Agents: "Perfect! We'll suggest 1:30pm at Fusion Bistro."
```

## 🛠️ Tool Stack

### **Core Technologies**
- **Python 3.10+** - Primary development language
- **FastAPI** - High-performance web framework for API endpoints
- **Uvicorn** - ASGI server for running FastAPI applications
- **SQLite** - Lightweight database for user preferences and agent data
- **uv** - Lightning-fast Python package manager

### **AI & LLM Integration**
- **Google Gemini (Vertex AI)** - Large language model for agent intelligence
- **Google ADK (Autonomous Developer Kit)** - Framework for building autonomous agents
- **Weights & Biases Weave** - Experiment tracking and model monitoring

### **Agent Communication**
- **A2A (Agent-to-Agent) Protocol** - Structured communication between agents
- **Python A2A Library** - Implementation of A2A protocol in Python
- **Registry Service** - Service discovery and health monitoring

### **Web Search & Data**
- **Exa API** - Intelligent web search with semantic understanding
- **Real-time Data Retrieval** - Live restaurant, concert, and event information

### **Frontend & UI**
- **HTML/CSS/JavaScript** - Modern web interface
- **Dark Theme UI** - Developer-friendly interface design
- **CORS Support** - Cross-origin resource sharing for frontend-backend communication

### **Development & Deployment**
- **Git** - Version control
- **Virtual Environments** - Isolated Python environments
- **Environment Variables** - Configuration management
- **Multi-service Architecture** - Distributed system design

## 🤖 Technology Stack

### 1. **Exa API** - Intelligent Web Search
**What it is:** A next-generation search API that understands context and can retrieve real-time information from the web.

**Why we use it:**
- **Semantic Understanding**: Exa understands natural language queries and context
- **Real-time Data**: Gets current information about restaurants, events, and services
- **Content Extraction**: Can pull detailed information from web pages
- **Multi-domain Search**: Searches across multiple platforms simultaneously

**In our project:**
- Restaurant agents use Exa to find current restaurant information, reviews, and availability
- Event agents use Exa to discover upcoming events and activities
- Personal agents use Exa to gather context about locations, services, and options

### 2. **A2A (Agent-to-Agent) Communication**
**What it is:** A protocol and framework for agents to communicate, negotiate, and collaborate with each other.

**Key Features:**
- **Structured Communication**: Agents exchange structured data about preferences and constraints
- **Negotiation Protocols**: Agents can negotiate when preferences conflict
- **Consensus Building**: Multiple agents work together to find optimal solutions
- **Privacy Controls**: Personal agents only share necessary information

**In our project:**
- Personal agents exchange preference summaries without revealing sensitive details
- Agents negotiate time slots, locations, and options
- Consensus is reached through iterative refinement

### 3. **ADK (Autonomous Developer Kit)**
**What it is:** A framework for building autonomous agents that can operate independently and make decisions.

**Key Features:**
- **Autonomous Decision Making**: Agents can make decisions without constant human oversight
- **Learning & Adaptation**: Agents learn from interactions and improve over time
- **Task Decomposition**: Complex tasks are broken down into manageable subtasks
- **Error Handling**: Robust error handling and fallback mechanisms

**In our project:**
- Personal agents autonomously manage their human's preferences and constraints
- Service agents (restaurant finder, event finder) operate independently
- Agents handle edge cases and errors gracefully

### 4. **Weights & Biases (W&B) Weave**
**What it is:** A framework for building, evaluating, and monitoring AI applications with built-in experiment tracking and model management.

**Key Features:**
- **Experiment Tracking**: Track different agent configurations and their performance
- **Model Monitoring**: Monitor agent performance and behavior in production
- **Collaborative Development**: Teams can work together on agent development
- **Reproducibility**: Ensure consistent results across different environments

**In our project:**
- Track how well agents collaborate and reach consensus
- Monitor restaurant recommendations and user satisfaction
- A/B test different agent communication protocols
- Ensure consistent behavior across different users and scenarios

## 🏗️ Architecture Overview

### Current System Architecture

```
┌─────────────────┐                                    ┌─────────────────┐
│   Frontend UI   │                                    │   Registry      │
│                 │                                    │   Service       │
│ • Chat Interface│                                    │                 │
│ • Network View  │                                    │ • Service       │
│ • User Management│                                   │   Discovery     │
│                 │                                    │ • Health Checks │
└─────────────────┘                                    └─────────────────┘
         │                                                       │
         │ HTTP/REST                                            │
         │                                                       │
         ▼                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Personal Agent │    │ Collaborative   │    │  Orchestrator   │
│                 │◄──►│  Middleware     │◄──►│   Service       │
│ • Chat Endpoint │    │                 │    │                 │
│ • Request Router│    │ • User Lookup   │    │ • Agent Mgmt    │
│ • Collaborative │    │ • Pref Merging  │    │ • Preferences   │
│   Detection     │    │ • Multi-user    │    │ • Database      │
│ • CORS Support  │    │   Coordination  │    │ • User Profiles │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                      │
         │                       │                      │
         │ A2A Protocol          │                      │
         │                       │                      │
         ▼                       ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Restaurant     │    │   Concert       │    │   Event         │
│  Selector       │    │   Selector      │    │   Selector      │
│                 │    │                 │    │                 │
│ • Cuisine Prefs │    │ • Genre Prefs   │    │ • Activity      │
│ • Dietary Restr │    │ • Venue Types   │    │   Matching      │
│ • Budget Filter │    │ • Time Windows  │    │ • Scheduling    │
│ • Location      │    │ • Artist Prefs  │    │ • Coordination  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Exa API     │
                    │  (Web Search)   │
                    │                 │
                    │ • Real-time     │
                    │   Restaurant    │
                    │   Data          │
                    │ • Concert Info  │
                    │ • Event Details │
                    └─────────────────┘
```

### Key Components

#### **Frontend UI**
- **Modern Web UI**: Dark theme with developer-friendly monospace fonts
- **Chat Interface**: Real-time chat with the personal agent
- **Network View**: Shows available users and their preferences
- **Collaborative Features**: Seamless multi-user request handling
- **Responsive Design**: Works across different screen sizes

#### **Personal Agent**
- **Request Detection**: Automatically detects collaborative, restaurant, and concert requests
- **Preference Management**: Stores and manages user preferences
- **A2A Communication**: Communicates with other agents using structured protocols
- **CORS Enabled**: Allows frontend connections from multiple origins
- **Context Awareness**: Maintains conversation context and user state

#### **Collaborative Middleware**
- **User Lookup**: Finds users by name/identifier in the database
- **Preference Merging**: Intelligently combines preferences from multiple users
  - Union for cuisines/genres
  - Intersection for dietary restrictions
  - Most conservative budget level
  - Combined atmosphere preferences
- **Multi-user Coordination**: Handles complex collaborative requests
- **Conflict Resolution**: Manages conflicting preferences between users

#### **Orchestrator Service**
- **Agent Management**: Creates and manages personal agents
- **User Database**: SQLite database with user profiles and preferences
- **Preference Storage**: Centralized preference management
- **Service Coordination**: Coordinates between different services
- **Demo Data**: Includes sample users and preferences for testing

#### **Selector Agents**
- **Restaurant Selector**: Finds restaurants based on merged preferences using Exa search
- **Concert Selector**: Discovers concerts and live music events with venue details
- **Event Selector**: Handles general event coordination and scheduling
- **Intelligent Filtering**: Uses AI to match preferences with available options

#### **Registry Service**
- **Service Discovery**: Maintains registry of all available agents
- **Health Monitoring**: Tracks agent health and availability
- **Load Balancing**: Distributes requests across available agents
- **Automatic Registration**: Agents self-register on startup

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) – lightning-fast Python package manager
- Exa API key (free tier is enough) – https://exa.ai
- Google Cloud project with Vertex AI / Gemini access  
  • Service-Account JSON key with "Generative AI User" role  
  • Environment variable `GOOGLE_APPLICATION_CREDENTIALS` pointing to the key file
- (Optional) Weights & Biases account for experiment tracking

### Gcloud help
(https://cloud.google.com/vertex-ai/generative-ai/docs/sdks/overview)
(https://cloud.google.com/vertex-ai/docs/general/iam-permissions)

### Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agent_networking
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   uv sync
   ```

4. **Activate the virtual environment**
   ```bash
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

5. **Set up environment variables**
   ```bash
   # Required
   export EXA_API_KEY="<your-exa-key>"
   export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
   export GOOGLE_CLOUD_LOCATION="us-central1"         # or your Gemini region
   export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/sa.json"
   export A2A_REGISTRY="http://localhost:9000"

   # Optional analytics
   export WANDB_API_KEY="<your-wandb-key>"
   ```

6. **Initialize W&B project**
   ```bash
   wandb init
   ```

### Development Setup

For development with additional tools:

```bash
# Install with development dependencies
uv sync --group dev

# Install with test dependencies
uv sync --group test

# Install with documentation dependencies
uv sync --group docs
```

### Running the Demo Agents

1. **Discovery Registry**  
   ```bash
   uv run python -m python_a2a.registry --host 0.0.0.0 --port 9000
   ```

2. **Restaurant Selector (port 8080)**  
   ```bash
   uv run uvicorn adk.restaurant_selector.A2A:app --host 0.0.0.0 --port 8080 --reload
   ```

3. **Personal Agents**  
   ```bash
   # Alice
   uv run python -m agents.personal_agent --name Alice --port 10001

   # Bob
   uv run python -m agents.personal_agent --name Bob --port 10002
   ```

4. **Test the full chain**  

   ```bash
   curl -X POST http://localhost:10001/invoke \
     -H "Content-Type: application/json" \
     -d '{
           "skill": "restaurant_recommendation",
           "input": {
             "location": "North Beach, San Francisco",
             "cuisines": ["japanese"],
             "diet": ["pescatarian"],
             "time_window": ["2025-07-15T18:00", "2025-07-15T21:00"],
             "budget": "high"
           }
         }'
   ```

#### Example Collaboration
```python
from adk import PersonalAgent, RestaurantAgent

# Create personal agents
alice_agent = PersonalAgent(user_id="alice", preferences=alice_prefs)
bob_agent = PersonalAgent(user_id="bob", preferences=bob_prefs)

# Collaborate to find lunch
restaurant_agent = RestaurantAgent()
result = await alice_agent.collaborate_with(
    bob_agent, 
    task="find_lunch_restaurant",
    restaurant_agent=restaurant_agent
)

print(f"Recommended: {result['restaurant']} at {result['time']}")
```

## 📊 Monitoring & Analytics

### W&B Dashboard
Track agent performance and collaboration metrics:
- **Consensus Success Rate**: How often agents reach agreement
- **User Satisfaction**: Feedback on recommendations
- **Agent Response Times**: Performance metrics
- **Collaboration Patterns**: How agents work together

### Example Metrics
```python
import wandb

wandb.init(project="agent-networking")

# Log collaboration metrics
wandb.log({
    "consensus_reached": True,
    "negotiation_rounds": 3,
    "user_satisfaction": 4.5,
    "response_time_seconds": 2.3
})
```

## 🔧 Configuration

### Personal Agent Preferences
```json
{
  "user_id": "alice",
  "preferences": {
    "food": {
      "cuisines": ["italian", "mediterranean"],
      "dietary_restrictions": ["vegetarian"],
      "price_range": {"min": 15, "max": 40},
      "atmosphere": ["quiet", "casual"]
    },
    "schedule": {
      "available_hours": ["12:00-14:00", "18:00-20:00"],
      "preferred_days": ["monday", "wednesday", "friday"]
    },
    "location": {
      "home": {"lat": 37.7749, "lng": -122.4194},
      "work": {"lat": 37.7849, "lng": -122.4094},
      "max_travel_time": 30
    }
  }
}
```

### A2A Communication Protocol
```python
# Example message format
{
  "from_agent": "alice_personal",
  "to_agent": "bob_personal",
  "message_type": "collaboration_request",
  "task": "find_lunch_restaurant",
  "constraints": {
    "time_window": "12:00-14:00",
    "location_radius": 5,
    "price_range": {"min": 15, "max": 40}
  },
  "preferences": {
    "cuisine": ["italian", "mediterranean"],
    "atmosphere": ["quiet"]
  }
}
```

## 🎯 Future Enhancements

### Phase 1: Core Collaboration
- [x] Basic personal agents
- [x] Restaurant finder agent
- [x] A2A communication protocol
- [ ] Event finder agent
- [ ] Schedule coordination

### Phase 2: Advanced Features
- [ ] Multi-person coordination (3+ people)
- [ ] Learning from user feedback
- [ ] Predictive preference modeling
- [ ] Real-time availability updates

### Phase 3: Ecosystem Expansion
- [ ] Travel planning agents
- [ ] Activity recommendation agents
- [ ] Business meeting coordination
- [ ] Social event planning

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run linting
uv run black adk/
uv run flake8 adk/
uv run mypy adk/

# Run all checks
uv run pre-commit run --all-files
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --group dev package-name

# Add a specific version
uv add "package-name>=1.0.0,<2.0.0"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Exa** for providing intelligent web search capabilities
- **Weights & Biases** for experiment tracking and monitoring
- **ADK Community** for the autonomous agent framework
- **A2A Protocol** contributors for agent communication standards
- **uv** for fast and reliable Python package management

---

**Built with ❤️ by the Agent Networking Team**

*Empowering individuals through collaborative AI agents* 