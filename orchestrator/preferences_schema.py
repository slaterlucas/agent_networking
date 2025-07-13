"""
Preferences schema for agent networking platform.

Defines the structure for capturing user preferences across multiple domains
that will be used to personalize their agent's behavior.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class DietaryRestriction(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    HALAL = "halal"
    KOSHER = "kosher"
    NONE = "none"


class BudgetLevel(str, Enum):
    LOW = "low"  # $, budget-conscious
    MEDIUM = "medium"  # $$, moderate spending
    HIGH = "high"  # $$$, premium experiences
    LUXURY = "luxury"  # $$$$, no budget constraints


class ActivityLevel(str, Enum):
    LOW = "low"  # Prefer quiet, relaxed activities
    MODERATE = "moderate"  # Mix of active and relaxed
    HIGH = "high"  # Very active, adventurous
    EXTREME = "extreme"  # Extreme sports, high adrenaline


class SocialPreference(str, Enum):
    INTIMATE = "intimate"  # Small groups, 1-4 people
    SMALL = "small"  # 5-10 people
    MEDIUM = "medium"  # 10-25 people
    LARGE = "large"  # 25+ people, big events
    FLEXIBLE = "flexible"  # Any size depending on context


# Individual preference domains
class FoodPreferences(BaseModel):
    cuisines: List[str] = Field(default_factory=list, description="Preferred cuisines (e.g., italian, japanese, mexican)")
    dietary_restrictions: List[DietaryRestriction] = Field(default_factory=list)
    favorite_dishes: List[str] = Field(default_factory=list, description="Specific dishes you love")
    dislikes: List[str] = Field(default_factory=list, description="Foods/ingredients to avoid")
    budget_level: BudgetLevel = BudgetLevel.MEDIUM
    dining_style: List[str] = Field(default_factory=list, description="e.g., casual, fine_dining, food_trucks, family_style")
    atmosphere_preferences: List[str] = Field(default_factory=list, description="e.g., quiet, lively, outdoor, cozy")


class MusicPreferences(BaseModel):
    genres: List[str] = Field(default_factory=list, description="Preferred music genres")
    artists: List[str] = Field(default_factory=list, description="Favorite artists/bands")
    instruments: List[str] = Field(default_factory=list, description="Instruments you play or love")
    concert_preferences: List[str] = Field(default_factory=list, description="e.g., intimate_venues, large_arenas, outdoor_festivals")
    discovery_openness: int = Field(default=5, ge=1, le=10, description="How open to new music (1-10)")


class SportsPreferences(BaseModel):
    favorite_teams: List[str] = Field(default_factory=list, description="Teams you follow")
    sports_to_watch: List[str] = Field(default_factory=list, description="Sports you enjoy watching")
    sports_to_play: List[str] = Field(default_factory=list, description="Sports you actively play")
    activity_level: ActivityLevel = ActivityLevel.MODERATE
    outdoor_vs_indoor: str = Field(default="both", description="outdoor, indoor, or both")


class EntertainmentPreferences(BaseModel):
    movie_genres: List[str] = Field(default_factory=list, description="Preferred movie genres")
    tv_shows: List[str] = Field(default_factory=list, description="Favorite TV shows/types")
    books: List[str] = Field(default_factory=list, description="Favorite books/genres")
    games: List[str] = Field(default_factory=list, description="Video games, board games, etc.")
    cultural_events: List[str] = Field(default_factory=list, description="museums, theater, art shows, etc.")


class ProfessionalPreferences(BaseModel):
    industry: str = Field(default="", description="Your industry/field")
    interests: List[str] = Field(default_factory=list, description="Professional interests/topics")
    networking_style: str = Field(default="balanced", description="casual, formal, or balanced")
    learning_preferences: List[str] = Field(default_factory=list, description="workshops, conferences, online, etc.")
    career_stage: str = Field(default="", description="student, early_career, mid_career, senior, executive")


class SocialPreferences(BaseModel):
    group_size_preference: SocialPreference = SocialPreference.FLEXIBLE
    communication_style: str = Field(default="balanced", description="introverted, extroverted, or balanced")
    meeting_style: List[str] = Field(default_factory=list, description="coffee, drinks, activities, meals, etc.")
    conversation_topics: List[str] = Field(default_factory=list, description="Topics you enjoy discussing")
    social_energy: int = Field(default=5, ge=1, le=10, description="How much social interaction you prefer (1-10)")


class LocationPreferences(BaseModel):
    home_location: str = Field(default="", description="Your primary location")
    preferred_areas: List[str] = Field(default_factory=list, description="Neighborhoods/areas you like")
    transportation: List[str] = Field(default_factory=list, description="car, public_transit, bike, walk, etc.")
    travel_willingness: int = Field(default=5, ge=1, le=10, description="How far you'll travel for activities (1-10)")


class TimePreferences(BaseModel):
    preferred_times: List[str] = Field(default_factory=list, description="morning, afternoon, evening, night")
    weekday_availability: List[str] = Field(default_factory=list, description="Days of week you're usually free")
    advance_planning: str = Field(default="flexible", description="last_minute, few_days, week_ahead, far_ahead")
    event_duration: List[str] = Field(default_factory=list, description="quick, short, medium, long, all_day")


# Main preferences container
class UserPreferences(BaseModel):
    """Complete user preferences across all domains."""
    
    # Core domains
    food: FoodPreferences = Field(default_factory=FoodPreferences)
    music: MusicPreferences = Field(default_factory=MusicPreferences)
    sports: SportsPreferences = Field(default_factory=SportsPreferences)
    entertainment: EntertainmentPreferences = Field(default_factory=EntertainmentPreferences)
    professional: ProfessionalPreferences = Field(default_factory=ProfessionalPreferences)
    social: SocialPreferences = Field(default_factory=SocialPreferences)
    location: LocationPreferences = Field(default_factory=LocationPreferences)
    time: TimePreferences = Field(default_factory=TimePreferences)
    
    # Meta preferences
    personality_traits: List[str] = Field(default_factory=list, description="adventurous, analytical, creative, etc.")
    values: List[str] = Field(default_factory=list, description="sustainability, authenticity, efficiency, etc.")
    communication_style: str = Field(default="friendly", description="formal, casual, friendly, professional")
    
    # Agent behavior preferences
    proactivity_level: int = Field(default=5, ge=1, le=10, description="How proactive should your agent be (1-10)")
    detail_preference: str = Field(default="balanced", description="minimal, balanced, detailed")
    confirmation_style: str = Field(default="ask", description="ask, suggest, decide")


def generate_system_prompt(preferences: UserPreferences) -> str:
    """Generate a system prompt for the personal agent based on user preferences."""
    
    prompt_parts = [
        "You are a highly personalized AI assistant. Your user has provided detailed preferences that shape how you should behave and make recommendations.",
        "",
        "## User Profile:",
    ]
    
    # Food preferences
    if preferences.food.cuisines or preferences.food.dietary_restrictions:
        prompt_parts.append("**Food & Dining:**")
        if preferences.food.cuisines:
            prompt_parts.append(f"- Preferred cuisines: {', '.join(preferences.food.cuisines)}")
        if preferences.food.dietary_restrictions:
            restrictions = [r.value for r in preferences.food.dietary_restrictions]
            prompt_parts.append(f"- Dietary restrictions: {', '.join(restrictions)}")
        if preferences.food.budget_level:
            prompt_parts.append(f"- Budget level: {preferences.food.budget_level.value}")
        if preferences.food.atmosphere_preferences:
            prompt_parts.append(f"- Preferred atmosphere: {', '.join(preferences.food.atmosphere_preferences)}")
        prompt_parts.append("")
    
    # Music preferences
    if preferences.music.genres or preferences.music.artists:
        prompt_parts.append("**Music & Entertainment:**")
        if preferences.music.genres:
            prompt_parts.append(f"- Music genres: {', '.join(preferences.music.genres)}")
        if preferences.music.artists:
            prompt_parts.append(f"- Favorite artists: {', '.join(preferences.music.artists)}")
        prompt_parts.append(f"- Openness to new music: {preferences.music.discovery_openness}/10")
        prompt_parts.append("")
    
    # Social preferences
    prompt_parts.append("**Social Style:**")
    prompt_parts.append(f"- Preferred group size: {preferences.social.group_size_preference.value}")
    prompt_parts.append(f"- Communication style: {preferences.social.communication_style}")
    prompt_parts.append(f"- Social energy level: {preferences.social.social_energy}/10")
    if preferences.social.conversation_topics:
        prompt_parts.append(f"- Enjoys discussing: {', '.join(preferences.social.conversation_topics)}")
    prompt_parts.append("")
    
    # Professional context
    if preferences.professional.industry or preferences.professional.interests:
        prompt_parts.append("**Professional Context:**")
        if preferences.professional.industry:
            prompt_parts.append(f"- Industry: {preferences.professional.industry}")
        if preferences.professional.career_stage:
            prompt_parts.append(f"- Career stage: {preferences.professional.career_stage}")
        if preferences.professional.interests:
            prompt_parts.append(f"- Professional interests: {', '.join(preferences.professional.interests)}")
        prompt_parts.append("")
    
    # Location and logistics
    if preferences.location.home_location:
        prompt_parts.append("**Location & Logistics:**")
        prompt_parts.append(f"- Home location: {preferences.location.home_location}")
        if preferences.location.preferred_areas:
            prompt_parts.append(f"- Preferred areas: {', '.join(preferences.location.preferred_areas)}")
        prompt_parts.append(f"- Travel willingness: {preferences.location.travel_willingness}/10")
        prompt_parts.append("")
    
    # Time preferences
    if preferences.time.preferred_times:
        prompt_parts.append("**Time Preferences:**")
        prompt_parts.append(f"- Preferred times: {', '.join(preferences.time.preferred_times)}")
        prompt_parts.append(f"- Planning style: {preferences.time.advance_planning}")
        prompt_parts.append("")
    
    # Personality and values
    if preferences.personality_traits or preferences.values:
        prompt_parts.append("**Personality & Values:**")
        if preferences.personality_traits:
            prompt_parts.append(f"- Personality traits: {', '.join(preferences.personality_traits)}")
        if preferences.values:
            prompt_parts.append(f"- Values: {', '.join(preferences.values)}")
        prompt_parts.append("")
    
    # Agent behavior instructions
    prompt_parts.extend([
        "## Behavior Guidelines:",
        f"- Proactivity level: {preferences.proactivity_level}/10 (1=reactive, 10=very proactive)",
        f"- Detail preference: {preferences.detail_preference}",
        f"- Confirmation style: {preferences.confirmation_style}",
        f"- Communication tone: {preferences.communication_style}",
        "",
        "## Instructions:",
        "- Always consider these preferences when making recommendations",
        "- Adapt your communication style to match the user's preferences",
        "- When planning activities or events, prioritize options that align with their interests",
        "- If preferences conflict or are unclear, ask for clarification",
        "- Be proactive in suggesting relevant opportunities based on their interests",
        "- Remember that preferences can evolve - be open to learning about changes"
    ])
    
    return "\n".join(prompt_parts)


# Interview steps configuration
INTERVIEW_STEPS = [
    {
        "id": "food",
        "title": "Food & Dining",
        "description": "Tell us about your food preferences and dining style",
        "fields": ["cuisines", "dietary_restrictions", "budget_level", "atmosphere_preferences"]
    },
    {
        "id": "music",
        "title": "Music & Entertainment", 
        "description": "What kind of music and entertainment do you enjoy?",
        "fields": ["genres", "artists", "concert_preferences", "discovery_openness"]
    },
    {
        "id": "social",
        "title": "Social Preferences",
        "description": "How do you like to socialize and interact with others?",
        "fields": ["group_size_preference", "communication_style", "social_energy", "conversation_topics"]
    },
    {
        "id": "professional",
        "title": "Professional Interests",
        "description": "Tell us about your work and professional interests",
        "fields": ["industry", "career_stage", "interests", "networking_style"]
    },
    {
        "id": "location_time",
        "title": "Location & Timing",
        "description": "Where are you based and when do you prefer activities?",
        "fields": ["home_location", "preferred_areas", "preferred_times", "advance_planning"]
    },
    {
        "id": "personality",
        "title": "Personality & Values",
        "description": "Help us understand your personality and what matters to you",
        "fields": ["personality_traits", "values", "communication_style", "proactivity_level"]
    }
] 