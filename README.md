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

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Person A's    │    │   Person B's    │    │   Person C's    │
│  Personal Agent │    │  Personal Agent │    │  Personal Agent │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   A2A Protocol  │
                    │   Coordinator   │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Restaurant     │    │   Event         │    │   Schedule      │
│  Finder Agent   │    │  Finder Agent   │    │  Coordinator    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Exa API     │
                    │  (Web Search)   │
                    └─────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Exa API key ([Get one here](https://exa.ai))
- Weights & Biases account ([Sign up here](https://wandb.ai))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agent_networking
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export EXA_API_KEY="your_exa_api_key"
   export WANDB_API_KEY="your_wandb_api_key"
   ```

4. **Initialize W&B project**
   ```bash
   wandb init
   ```

### Running the Agents

#### Start Personal Agents
```bash
python -m adk.personal_agent --user_id user_a --preferences preferences_a.json
python -m adk.personal_agent --user_id user_b --preferences preferences_b.json
```

#### Start Service Agents
```bash
python -m adk.restaurant_selector
python -m adk.event_selector
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
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 adk/
black adk/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Exa** for providing intelligent web search capabilities
- **Weights & Biases** for experiment tracking and monitoring
- **ADK Community** for the autonomous agent framework
- **A2A Protocol** contributors for agent communication standards

---

**Built with ❤️ by the Agent Networking Team**

*Empowering individuals through collaborative AI agents* 