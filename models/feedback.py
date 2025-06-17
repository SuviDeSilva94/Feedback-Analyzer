# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime

# class CustomerInfo(BaseModel):
#     name: str
#     phone: str
#     email: Optional[str] = None

# class FeedbackRequest(BaseModel):
#     text: str
#     customer: CustomerInfo
#     rating: Optional[int] = Field(None, ge=1, le=5)
#     category: Optional[str] = None

# class FeedbackResponse(BaseModel):
#     id: str
#     text: str
#     sentiment: str
#     topic: str
#     customer: CustomerInfo
#     rating: Optional[int] = None
#     category: Optional[str] = None
#     created_at: datetime
#     analysis: dict

# class FeedbackStats(BaseModel):
#     total: int
#     sentiment_distribution: List[dict]
#     topic_distribution: List[dict] 