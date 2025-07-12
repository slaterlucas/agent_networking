# ADK Agents with Exa Integration

This repository contains two Autonomous Developer Kit (ADK) agents integrated with the Exa API for intelligent search and selection tasks.

## 🤖 Agents

### 1. Event Selector Agent
Located in `event_selector/`
- **Purpose**: Searches and selects events based on user criteria
- **Features**:
  - Event discovery using Exa API
  - Intelligent filtering by location, type, price, and date
  - Supports multiple event platforms (Eventbrite, Meetup, Facebook, etc.)
  - Configurable search parameters

### 2. Restaurant Selector Agent
Located in `restaurant_selector/`
- **Purpose**: Searches and selects restaurants based on user preferences
- **Features**:
  - Restaurant discovery using Exa API
  - Cuisine type filtering
  - Dietary restriction support
  - Price range and rating filtering
  - Detailed content retrieval

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Exa API key (get one at [exa.ai](https://exa.ai))

### Installation

1. **Clone and navigate to the ADK directory**
   ```bash
   cd adk
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export EXA_API_KEY="your_exa_api_key_here"
   ```

### Running the Agents

#### Event Selector Agent
```bash
cd event_selector
python main.py
```

#### Restaurant Selector Agent
```bash
cd restaurant_selector
python main.py
```

## 📁 Directory Structure

```
adk/
├── README.md
├── requirements.txt
├── event_selector/
│   ├── main.py
│   └── config.json
└── restaurant_selector/
    ├── main.py
    └── config.json
```

## 🛠️ Configuration

Each agent has its own `config.json` file with customizable parameters:

### Event Selector Configuration
- `search_params`: Exa API search parameters
- `event_types`: Supported event categories
- `location_radius`: Search radius in miles
- `price_range`: Price filtering options
- `preferred_domains`: Event platforms to search

### Restaurant Selector Configuration
- `search_params`: Exa API search parameters
- `cuisine_types`: Supported cuisine categories
- `dietary_restrictions`: Dietary preference options
- `distance_radius`: Search radius in miles
- `rating_threshold`: Minimum rating filter

## 🔧 Usage Examples

### Event Selector Agent
```python
from main import EventSelectorAgent

agent = EventSelectorAgent()
results = await agent.run(
    user_query="tech conferences",
    location="San Francisco",
    event_type="conference",
    criteria={"price_range": {"min": 0, "max": 200}}
)
```

### Restaurant Selector Agent
```python
from main import RestaurantSelectorAgent

agent = RestaurantSelectorAgent()
results = await agent.run(
    user_query="Italian restaurants",
    location="New York City",
    cuisine="Italian",
    criteria={"dietary_restrictions": ["vegetarian"]}
)
```

## 🔍 Exa API Integration

Both agents leverage the Exa API for:
- **Semantic Search**: Understanding natural language queries
- **Web Content Retrieval**: Fetching detailed information
- **Domain-Specific Filtering**: Targeting relevant platforms
- **Real-time Results**: Getting up-to-date information

### Key Exa Features Used:
- `exa.search()`: Primary search functionality
- `exa.get_contents()`: Detailed content retrieval
- `include_domains`: Platform-specific searches
- `use_autoprompt`: Enhanced query understanding

## 🎯 Features

### Event Selector Agent
- ✅ Multi-platform event discovery
- ✅ Date range filtering
- ✅ Location-based search
- ✅ Price range filtering
- ✅ Event type categorization
- ✅ Relevance scoring

### Restaurant Selector Agent
- ✅ Multi-platform restaurant discovery
- ✅ Cuisine type filtering
- ✅ Dietary restriction support
- ✅ Price and rating filtering
- ✅ Detailed restaurant information
- ✅ Location-based search

## 🔒 Environment Variables

Create a `.env` file in the root directory:
```env
EXA_API_KEY=your_exa_api_key_here
AGENT_LOG_LEVEL=INFO
AGENT_TIMEOUT=30
EVENT_AGENT_DEFAULT_LOCATION=San Francisco
RESTAURANT_AGENT_DEFAULT_LOCATION=New York City
```

## 📝 Customization

### Adding New Event Types
Edit `event_selector/config.json` and add to the `event_types` array:
```json
{
  "event_types": [
    "conference",
    "workshop",
    "your_new_event_type"
  ]
}
```

### Adding New Cuisine Types
Edit `restaurant_selector/config.json` and add to the `cuisine_types` array:
```json
{
  "cuisine_types": [
    "italian",
    "japanese",
    "your_new_cuisine"
  ]
}
```

### Adding New Search Domains
Update the `preferred_domains` array in either agent's config file:
```json
{
  "preferred_domains": [
    "existing-domain.com",
    "new-domain.com"
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the configuration files
- Verify your Exa API key
- Review the error logs
- Open an issue on GitHub

---

**Built with ❤️ using ADK and Exa API** 