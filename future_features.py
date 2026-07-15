from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum

# This file outlines the structure for future API features.
# It contains Pydantic models for request/response bodies and
# placeholder functions for the business logic.
# The actual implementation (e.g., LLM calls, database queries)
# will be added later.

# --- Enums for Future Schemas ---
class PriorityEnum(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class TeamEnum(str, Enum):
    Billing_Team = "Billing Team"
    Support_Team = "Support Team"
    Delivery_Team = "Delivery Team"
    Technical_Team = "Technical Team"

class SocialPlatformEnum(str, Enum):
    Twitter_X = "Twitter/X"
    Instagram = "Instagram"
    Facebook = "Facebook"
    Reddit = "Reddit"

# --- 1. Schemas for Future APIs ---

# 14. Voice Review API
# Note: Input will likely be a file upload handled by FastAPI.
# The process is: Audio -> Speech-to-Text -> Analysis.
class VoiceAnalysisResponse(BaseModel):
    transcript: str = Field(description="The text transcribed from the audio.")
    sentiment: str
    summary: str
    ai_reply: str

# 15. Email Analysis API
class EmailAnalysisResponse(BaseModel):
    priority: PriorityEnum
    summary: str
    suggested_reply: str
    department: TeamEnum

# 16. Social Media API
class SocialMediaPostAnalysis(BaseModel):
    platform: SocialPlatformEnum
    sentiment: str
    summary: str
    top_comment_themes: List[str]

# 17. Competitor Comparison API
class CompetitorComparisonResponse(BaseModel):
    company_a_loves: List[str] = Field(description="What customers love about Company A.")
    company_a_hates: List[str] = Field(description="What customers hate about Company A.")
    company_b_loves: List[str] = Field(description="What customers love about Company B.")
    company_b_hates: List[str] = Field(description="What customers hate about Company B.")
    comparison_summary: str = Field(description="An AI-generated summary comparing the two.")
    company_a_strengths: List[str]
    company_a_weaknesses: List[str]
    company_b_strengths: List[str]
    company_b_weaknesses: List[str]

# 18. Dashboard API
class DashboardAnalyticsResponse(BaseModel):
    weekly_sentiment_trend: float = Field(description="Sentiment score trend over the last 7 days.")
    monthly_trend: float = Field(description="Sentiment score trend over the last 30 days.")
    complaint_ratio: float = Field(description="The ratio of negative to positive reviews.")
    happy_customer_percentage: float
    top_issues: List[str]
    average_rating_prediction: float = Field(ge=1, le=5)

# 19. Webhook Schemas
class WebhookEventEnum(str, Enum):
    Negative_Review = "Negative Review"
    High_Urgency = "High Urgency"
    Spam_Detected = "Spam Detected"

class WebhookConfig(BaseModel):
    """Defines a webhook to be triggered on a specific event."""
    event: WebhookEventEnum = Field(description="The event that triggers the webhook.")
    target_url: str = Field(description="The URL to which the webhook payload will be sent.")


# --- 2. Placeholder Functions for Future Implementation ---

def process_voice_review(audio_file: bytes) -> VoiceAnalysisResponse:
    """
    1. Transcribe audio to text (e.g., using OpenAI Whisper).
    2. Analyze the transcript for sentiment, summary, and reply.
    """
    pass

def analyze_customer_email(email_body: str) -> EmailAnalysisResponse:
    """
    Analyze the content of a customer email to determine priority,
    create a summary, suggest a reply, and assign a department.
    """
    pass

def analyze_social_media_post(
    post_text: str, platform: SocialPlatformEnum
) -> SocialMediaPostAnalysis:
    """
    Analyze a social media post and its comments to extract overall sentiment and themes.
    """
    pass

def compare_competitors(
    reviews_a: List[str], reviews_b: List[str]
) -> CompetitorComparisonResponse:
    """
    Takes two lists of reviews and performs a comparative analysis
    to identify strengths, weaknesses, and customer preferences for each.
    """
    pass

def get_dashboard_analytics() -> DashboardAnalyticsResponse:
    """
    This function will likely query a database where reviews and their
    analyses are stored over time to generate trend data.
    The implementation is deferred.
    """
    pass

def trigger_webhooks_for_event(event_type: str, analysis_data: dict):
    """
    Finds all registered webhooks for a given event and sends a payload.

    Future Implementation Steps:
    1. Query a database for all WebhookConfig objects matching the `event_type`.
    2. For each webhook found, send an HTTP POST request to its `target_url`.
    3. The body of the request should be the `analysis_data` payload.
    4. Implement retry logic and logging for failed webhook deliveries.
    """
    print(f"--- (Placeholder) Webhook triggered for event: {event_type} ---")
    pass