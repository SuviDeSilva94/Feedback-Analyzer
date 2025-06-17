from pydantic import BaseModel, Field

class NotificationData(BaseModel):
    feedback_id: str
    customer_name: str
    customer_phone: str
    sentiment_score: float
    main_topic: str
    feedback_text: str
    type: str = Field(default="negative_feedback") 