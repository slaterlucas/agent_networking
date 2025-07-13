from agents.user_agent_template import create_user_agent, UserProfile

user_profile = UserProfile(
    name="Charlie",
    preferences="I'm into fitness, yoga, and healthy living. I enjoy nature walks and meditation.",
    location="San Francisco",
    budget="medium",
    dietary_restrictions=["vegan"],
    cuisine_preferences=["Thai", "Vegan"],
    interests=["fitness", "yoga", "meditation"],
    agent_port=10005
)

app = create_user_agent(user_profile) 