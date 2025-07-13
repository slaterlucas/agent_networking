from agents.user_agent_template import create_user_agent, UserProfile

user_profile = UserProfile(
    name="Bob",
    preferences="I enjoy cooking, trying new recipes, and exploring different cuisines. I love traveling and photography.",
    location="San Francisco",
    budget="medium",
    dietary_restrictions=["none"],
    cuisine_preferences=["Mexican", "Indian"],
    interests=["cooking", "travel", "photography"],
    agent_port=10004
)

app = create_user_agent(user_profile) 