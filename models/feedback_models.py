from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId

class CustomerData(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Customer's full name")
    phone: str = Field(..., min_length=10, max_length=15, description="Customer's phone number")

class FeedbackRequest(BaseModel):
    feedback_text: str = Field(..., min_length=1, max_length=1000, description="Feedback text to analyze")
    customer: CustomerData = Field(..., description="Customer information")

class CustomerResponse(BaseModel):
    name: str
    phone: str

class FeedbackResponse(BaseModel):
    id: str
    text: str
    customer: Optional[CustomerResponse] = None
    customer_id: Optional[str] = None
    sentiment: str
    sentiment_scores: Dict[str, float]
    main_topic: str
    topic_scores: Dict[str, float]
    top_topics: List[str]
    created_at: datetime

    class Config:
        json_encoders = {
            ObjectId: str
        }

class FeedbackStats(BaseModel):
    total_feedback: int
    sentiment_distribution: Dict[str, int] = Field(
        default_factory=lambda: {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
    )
    topic_distribution: Dict[str, int] = Field(
        default_factory=lambda: {
            "product_quality": 0,
            "customer_service": 0,
            "delivery": 0,
            "pricing": 0,
            "usability": 0
        }
    ) 