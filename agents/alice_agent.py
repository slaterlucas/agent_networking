from agents.user_agent_template import create_user_agent, UserProfile

user_profile = UserProfile(
    name="Alice",
    preferences="I love technology, programming, and outdoor activities",
    location="San Francisco",
    budget="medium",
    dietary_restrictions=["vegetarian"],
    cuisine_preferences=["Italian", "Asian"],
    interests=["technology", "programming", "hiking"],
    agent_port=10003
)

app = create_user_agent(user_profile) 