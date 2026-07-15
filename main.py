import strawberry
from langchain_openai import ChatOpenAI
from typing import List, Literal, Optional
from enum import Enum
import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from strawberry.fastapi import GraphQLRouter

load_dotenv()

# --- 1. LLM and Model Configuration ---

model = ChatOpenAI(
    model_name="openrouter/free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

# --- 2. Pydantic Schemas for API and LLM Output ---

# Define Enums to replace all Literal types for Strawberry compatibility
class SentimentEnum(str, Enum):
    Positive = "Positive"
    Negative = "Negative"
    Neutral = "Neutral"
    Mixed = "Mixed"

class EmotionEnum(str, Enum):
    Angry = "Angry"
    Happy = "Happy"
    Excited = "Excited"
    Frustrated = "Frustrated"
    Sad = "Sad"
    Confused = "Confused"

class UrgencyEnum(str, Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"

class CriticalUrgencyEnum(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"

class CategoryEnum(str, Enum):
    Delivery = "Delivery"
    Pricing = "Pricing"
    Payment = "Payment"
    Refund = "Refund"
    Customer_Support = "Customer Support"
    Quality = "Quality"
    App = "App"
    Website = "Website"
    Shipping = "Shipping"

class SpamTypeEnum(str, Enum):
    Fake_review = "Fake review"
    Bot_review = "Bot review"
    Repeated_review = "Repeated review"
    Promotional_review = "Promotional review"

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

class ToxicityTypeEnum(str, Enum):
    Abusive = "Abusive"
    Threat = "Threat"
    Hate = "Hate"
    Profanity = "Profanity"
    Harassment = "Harassment"

class ActionEnum(str, Enum):
    Reply_publicly = "Reply publicly"
    Offer_discount = "Offer discount"
    Escalate_to_support = "Escalate to support"
    No_action_needed = "No action needed"


# Schemas for individual APIs
class SentimentResponse(BaseModel):
    sentiment: SentimentEnum
    confidence: float = Field(ge=0, le=1)

class EmotionResponse(BaseModel):
    emotions: List[EmotionEnum]

# Master schema for the /analyze endpoint
class FullAnalysis(BaseModel):
    """A complete analysis of a piece of customer feedback."""
    sentiment: SentimentEnum = Field(description="Overall sentiment of the text.")
    confidence: float = Field(description="Confidence score for the sentiment prediction, from 0.0 to 1.0.")
    emotions: List[str] = Field(description="List of emotions detected in the text.")
    urgency: UrgencyEnum = Field(description="The urgency level of the feedback.")
    category: str = Field(description="A single, most relevant category for the feedback (e.g., 'Delivery', 'Customer Support', 'Billing').")
    summary: str = Field(description="A concise, one-sentence summary of the customer's feedback.")
    requires_human: bool = Field(description="Whether the feedback requires a human to review it. True for complex issues, high urgency, or strong negative emotion.")

# --- Schemas for New APIs ---
class ReviewSummaryResponse(BaseModel):
    top_complaints: List[str] = Field(description="A list of the most common complaints found in the reviews.")
    top_praises: List[str] = Field(description="A list of the most common points of praise found in the reviews.")
    trending_issues: List[str] = Field(description="A list of emerging or trending issues mentioned.")
    ai_summary: str = Field(description="A high-level AI-generated summary of all reviews provided.")

class CategoryResponse(BaseModel):
    category: CategoryEnum

class SpamResponse(BaseModel):
    is_spam: bool = Field(description="True if the review is likely spam.")
    spam_type: Optional[SpamTypeEnum] = Field(description="The type of spam if detected.")

class UrgencyResponse(BaseModel):
    urgency: CriticalUrgencyEnum

class PriorityResponse(BaseModel):
    priority: PriorityEnum

class TeamAssignmentResponse(BaseModel):
    team: TeamEnum

class MultiLanguageResponse(BaseModel):
    english_summary: str
    english_response: str

class KeywordsResponse(BaseModel):
    keywords: List[str]

class Aspect(BaseModel):
    aspect: str = Field(description="The specific feature or topic being discussed, e.g., 'Food', 'Service'.")
    sentiment: SentimentEnum = Field(description="The sentiment towards this specific aspect.")

class AspectSentimentResponse(BaseModel):
    aspects: List[Aspect]

class ToxicityResponse(BaseModel):
    is_toxic: bool
    toxicity_types: List[ToxicityTypeEnum]

class ActionableInsights(BaseModel):
    """Provides AI-suggested next steps for a piece of feedback."""
    recommended_action: ActionEnum = Field(description="The single best next action to take.")
    priority: PriorityEnum = Field(description="The priority level for this feedback.")
    escalate: bool = Field(description="Whether this issue should be escalated to a senior team member.")
    estimated_customer_satisfaction: float = Field(description="A predicted customer satisfaction score (0.0 to 1.0) if the recommended action is taken.", ge=0, le=1)


# --- 3. Structured LLM Models ---

structured_analyzer = model.with_structured_output(FullAnalysis)
structured_sentiment = model.with_structured_output(SentimentResponse)
structured_emotion = model.with_structured_output(EmotionResponse)
structured_summarizer = model.with_structured_output(ReviewSummaryResponse)
structured_categorizer = model.with_structured_output(CategoryResponse)
structured_spam_detector = model.with_structured_output(SpamResponse)
structured_urgency_detector = model.with_structured_output(UrgencyResponse)
structured_priority_assigner = model.with_structured_output(PriorityResponse)
structured_team_assigner = model.with_structured_output(TeamAssignmentResponse)
structured_translator = model.with_structured_output(MultiLanguageResponse)
structured_keyword_extractor = model.with_structured_output(KeywordsResponse)
structured_aspect_sentiment = model.with_structured_output(AspectSentimentResponse)
structured_toxicity_detector = model.with_structured_output(ToxicityResponse)
structured_actions_model = model.with_structured_output(ActionableInsights)

# --- 4. API Logic Functions ---

def get_full_analysis(text: str) -> FullAnalysis:
    prompt = f"""Analyze the following customer feedback text and extract all required fields.
    Feedback: "{text}"
    """
    return structured_analyzer.invoke(prompt)

def get_sentiment(text: str) -> SentimentResponse:
    prompt = f"""Analyze the sentiment of the following text.
    Text: "{text}"
    """
    return structured_sentiment.invoke(prompt)

def get_emotions(text: str) -> EmotionResponse:
    prompt = f"""Detect the primary emotions in the following text.
    Text: "{text}"
    """
    return structured_emotion.invoke(prompt)

def generate_reply(text: str, tone: str) -> str:
    prompt = f"""You are a customer support agent. A customer wrote the following:
    
    "{text}"
    
    Write a response to the customer. Your response should have a {tone} tone.
    """
    return model.invoke(prompt).content

def summarize_reviews(reviews: List[str]) -> ReviewSummaryResponse:
    reviews_text = "\n- ".join(reviews)
    prompt = f"Analyze the following batch of customer reviews and provide a summary including top complaints, top praises, and trending issues.\n\nReviews:\n- {reviews_text}"
    return structured_summarizer.invoke(prompt)

def get_category(text: str) -> CategoryResponse:
    prompt = f"Categorize the following review into one of the predefined categories.\nReview: '{text}'"
    return structured_categorizer.invoke(prompt)

def detect_spam(text: str) -> SpamResponse:
    prompt = f"Analyze the following review to determine if it is spam. If it is, classify the spam type.\nReview: '{text}'"
    return structured_spam_detector.invoke(prompt)

def get_urgency(text: str) -> UrgencyResponse:
    prompt = f"Determine the urgency of this customer feedback.\nFeedback: '{text}'"
    return structured_urgency_detector.invoke(prompt)

def get_priority(text: str) -> PriorityResponse:
    prompt = f"Based on the content and urgency of this review, assign a ticket priority (P1-P4).\nReview: '{text}'"
    return structured_priority_assigner.invoke(prompt)

def assign_team(text: str) -> TeamAssignmentResponse:
    prompt = f"Read the following customer issue and assign it to the correct team.\nIssue: '{text}'"
    return structured_team_assigner.invoke(prompt)

def translate_and_respond(text: str) -> MultiLanguageResponse:
    prompt = f"The following text is in a foreign language. First, provide a concise one-sentence summary in English. Second, write a helpful and professional response in English.\n\nForeign Text: '{text}'"
    return structured_translator.invoke(prompt)

def extract_keywords(text: str) -> KeywordsResponse:
    prompt = f"Extract the most important keywords and key phrases from the following text.\nText: '{text}'"
    return structured_keyword_extractor.invoke(prompt)

def get_aspect_sentiment(text: str) -> AspectSentimentResponse:
    prompt = f"""Analyze the following review to identify different aspects (like 'Food', 'Service', 'Price') and determine the sentiment for each aspect.
    
    Example:
    Review: "The pizza was delicious but the delivery driver was rude."
    Aspects: [{{'aspect': 'Pizza', 'sentiment': 'Positive'}}, {{'aspect': 'Delivery Driver', 'sentiment': 'Negative'}}]
    
    Now, analyze this review:
    Review: '{text}'
    """
    return structured_aspect_sentiment.invoke(prompt)

def detect_toxicity(text: str) -> ToxicityResponse:
    prompt = f"Analyze the following text for any toxic content like abuse, threats, or hate speech. List all categories that apply.\nText: '{text}'"
    return structured_toxicity_detector.invoke(prompt)

def get_suggested_actions(text: str) -> ActionableInsights:
    prompt = f"""Based on the following customer feedback, provide actionable insights: recommend an action, set a priority, decide if it needs escalation, and estimate customer satisfaction if the action is taken.
    Feedback: '{text}'"""
    return structured_actions_model.invoke(prompt)

# --- 5. FastAPI REST API Endpoints ---

app = FastAPI(
    title="AI Customer Feedback API",
    description="One API that accepts customer text and returns everything a company needs.",
)

class AnalyzeRequest(BaseModel):
    text: str

class ReplyRequest(BaseModel):
    text: str
    tone: Literal["Friendly", "Professional", "Luxury", "Startup", "Legal", "Technical"] = "Professional"

class SummarizeRequest(BaseModel):
    reviews: List[str]

@app.post("/analyze", response_model=FullAnalysis)
def analyze_endpoint(request: AnalyzeRequest):
    """Performs a full analysis of the customer feedback."""
    return get_full_analysis(request.text)

@app.post("/sentiment", response_model=SentimentResponse)
def sentiment_endpoint(request: AnalyzeRequest):
    """Detects the sentiment of a piece of text."""
    return get_sentiment(request.text)

@app.post("/emotion", response_model=EmotionResponse)
def emotion_endpoint(request: AnalyzeRequest):
    """Detects emotions in a piece of text."""
    return get_emotions(request.text)

@app.post("/reply", response_model=str)
def reply_endpoint(request: ReplyRequest):
    """Generates an AI-powered reply with a specific tone."""
    return generate_reply(request.text, request.tone)

@app.post("/summarize-reviews", response_model=ReviewSummaryResponse)
def summarize_endpoint(request: SummarizeRequest):
    """Analyzes a batch of reviews and provides a high-level summary."""
    return summarize_reviews(request.reviews)

@app.post("/categorize", response_model=CategoryResponse)
def categorize_endpoint(request: AnalyzeRequest):
    """Categorizes a single review."""
    return get_category(request.text)

@app.post("/detect-spam", response_model=SpamResponse)
def spam_endpoint(request: AnalyzeRequest):
    """Detects if a review is spam."""
    return detect_spam(request.text)

@app.post("/detect-urgency", response_model=UrgencyResponse)
def urgency_endpoint(request: AnalyzeRequest):
    """Detects the urgency of a review."""
    return get_urgency(request.text)

@app.post("/assign-priority", response_model=PriorityResponse)
def priority_endpoint(request: AnalyzeRequest):
    """Assigns a ticket priority to a review."""
    return get_priority(request.text)

@app.post("/assign-team", response_model=TeamAssignmentResponse)
def team_assignment_endpoint(request: AnalyzeRequest):
    """Assigns a review to the appropriate team."""
    return assign_team(request.text)

@app.post("/multi-language", response_model=MultiLanguageResponse)
def multi_language_endpoint(request: AnalyzeRequest):
    """Provides an English summary and response for non-English text."""
    return translate_and_respond(request.text)

@app.post("/extract-keywords", response_model=KeywordsResponse)
def keywords_endpoint(request: AnalyzeRequest):
    """Extracts keywords from a review."""
    return extract_keywords(request.text)

@app.post("/aspect-sentiment", response_model=AspectSentimentResponse)
def aspect_sentiment_endpoint(request: AnalyzeRequest):
    """Performs aspect-based sentiment analysis."""
    return get_aspect_sentiment(request.text)

@app.post("/detect-toxicity", response_model=ToxicityResponse)
def toxicity_endpoint(request: AnalyzeRequest):
    """Detects toxic content in a review."""
    return detect_toxicity(request.text)

@app.post("/actions", response_model=ActionableInsights)
def actions_endpoint(request: AnalyzeRequest):
    """Generates AI-suggested actions for a piece of feedback."""
    return get_suggested_actions(request.text)

# --- 6. GraphQL API using Strawberry ---

# Convert Pydantic models to Strawberry types
@strawberry.experimental.pydantic.type(model=FullAnalysis)
class FullAnalysisType:
    sentiment: strawberry.auto
    confidence: strawberry.auto
    emotions: strawberry.auto
    urgency: strawberry.auto
    category: strawberry.auto
    summary: strawberry.auto
    requires_human: strawberry.auto

@strawberry.experimental.pydantic.type(model=SentimentResponse)
class SentimentResponseType:
    sentiment: strawberry.auto
    confidence: strawberry.auto

@strawberry.experimental.pydantic.type(model=EmotionResponse)
class EmotionResponseType:
    emotions: strawberry.auto

@strawberry.experimental.pydantic.type(model=ReviewSummaryResponse)
class ReviewSummaryResponseType:
    top_complaints: strawberry.auto
    top_praises: strawberry.auto
    trending_issues: strawberry.auto
    ai_summary: strawberry.auto

@strawberry.experimental.pydantic.type(model=CategoryResponse)
class CategoryResponseType:
    category: strawberry.auto

@strawberry.experimental.pydantic.type(model=SpamResponse)
class SpamResponseType:
    is_spam: strawberry.auto
    spam_type: strawberry.auto

@strawberry.experimental.pydantic.type(model=UrgencyResponse)
class UrgencyResponseType:
    urgency: strawberry.auto

@strawberry.experimental.pydantic.type(model=PriorityResponse)
class PriorityResponseType:
    priority: strawberry.auto

@strawberry.experimental.pydantic.type(model=TeamAssignmentResponse)
class TeamAssignmentResponseType:
    team: strawberry.auto

@strawberry.experimental.pydantic.type(model=MultiLanguageResponse)
class MultiLanguageResponseType:
    english_summary: strawberry.auto
    english_response: strawberry.auto

@strawberry.experimental.pydantic.type(model=KeywordsResponse)
class KeywordsResponseType:
    keywords: strawberry.auto

@strawberry.experimental.pydantic.type(model=Aspect)
class AspectType:
    aspect: strawberry.auto
    sentiment: strawberry.auto

@strawberry.experimental.pydantic.type(model=AspectSentimentResponse)
class AspectSentimentResponseType:
    aspects: strawberry.auto

@strawberry.experimental.pydantic.type(model=ToxicityResponse)
class ToxicityResponseType:
    is_toxic: strawberry.auto
    toxicity_types: strawberry.auto

@strawberry.experimental.pydantic.type(model=ActionableInsights)
class ActionableInsightsType:
    pass # Fields will be added if needed, but this is for REST first

@strawberry.type
class Query:
    @strawberry.field
    def analyze(self, text: str) -> FullAnalysisType:
        """Performs a full analysis of the customer feedback."""
        analysis_data = get_full_analysis(text)
        return FullAnalysisType.from_pydantic(analysis_data)

    @strawberry.field
    def sentiment(self, text: str) -> SentimentResponseType:
        """Detects the sentiment of a piece of text."""
        sentiment_data = get_sentiment(text)
        return SentimentResponseType.from_pydantic(sentiment_data)

    @strawberry.field
    def emotion(self, text: str) -> EmotionResponseType:
        """Detects emotions in a piece of text."""
        emotion_data = get_emotions(text)
        return EmotionResponseType.from_pydantic(emotion_data)

    @strawberry.field
    def reply(self, text: str, tone: str) -> str:
        """Generates an AI-powered reply with a specific tone."""
        return generate_reply(text, tone)

    @strawberry.field
    def summarize_reviews(self, reviews: List[str]) -> ReviewSummaryResponseType:
        """Analyzes a batch of reviews and provides a high-level summary."""
        summary_data = summarize_reviews(reviews)
        return ReviewSummaryResponseType.from_pydantic(summary_data)

    @strawberry.field
    def categorize(self, text: str) -> CategoryResponseType:
        """Categorizes a single review."""
        category_data = get_category(text)
        return CategoryResponseType.from_pydantic(category_data)

    @strawberry.field
    def detect_spam(self, text: str) -> SpamResponseType:
        """Detects if a review is spam."""
        spam_data = detect_spam(text)
        return SpamResponseType.from_pydantic(spam_data)

    @strawberry.field
    def detect_urgency(self, text: str) -> UrgencyResponseType:
        """Detects the urgency of a review."""
        urgency_data = get_urgency(text)
        return UrgencyResponseType.from_pydantic(urgency_data)

    @strawberry.field
    def assign_priority(self, text: str) -> PriorityResponseType:
        """Assigns a ticket priority to a review."""
        priority_data = get_priority(text)
        return PriorityResponseType.from_pydantic(priority_data)

    @strawberry.field
    def assign_team(self, text: str) -> TeamAssignmentResponseType:
        """Assigns a review to the appropriate team."""
        team_data = assign_team(text)
        return TeamAssignmentResponseType.from_pydantic(team_data)

    @strawberry.field
    def multi_language(self, text: str) -> MultiLanguageResponseType:
        """Provides an English summary and response for non-English text."""
        data = translate_and_respond(text)
        return MultiLanguageResponseType.from_pydantic(data)

    @strawberry.field
    def extract_keywords(self, text: str) -> KeywordsResponseType:
        """Extracts keywords from a review."""
        data = extract_keywords(text)
        return KeywordsResponseType.from_pydantic(data)

    @strawberry.field
    def aspect_sentiment(self, text: str) -> AspectSentimentResponseType:
        """Performs aspect-based sentiment analysis."""
        data = get_aspect_sentiment(text)
        return AspectSentimentResponseType.from_pydantic(data)

    @strawberry.field
    def detect_toxicity(self, text: str) -> ToxicityResponseType:
        """Detects toxic content in a review."""
        data = detect_toxicity(text)
        return ToxicityResponseType.from_pydantic(data)

    @strawberry.field
    def actions(self, text: str) -> ActionableInsightsType:
        """Generates AI-suggested actions for a piece of feedback."""
        data = get_suggested_actions(text)
        return ActionableInsightsType.from_pydantic(data)

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# --- 7. Run the API Server ---

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)