import pytest
from unittest.mock import Mock
from datetime import datetime
from bson import ObjectId

@pytest.fixture
def mock_feedback_data():
    return {
        "text": "Great product!",
        "customer": {
            "name": "Test User",
            "phone": "1234567890"
        },
        "sentiment": "positive",
        "sentiment_scores": {
            "positive": 0.8,
            "negative": 0.2
        },
        "main_topic": "product_quality",
        "topic_scores": {
            "product_quality": 0.6,
            "customer_service": 0.2,
            "delivery": 0.1,
            "pricing": 0.05,
            "usability": 0.05
        },
        "top_topics": ["product_quality", "customer_service"],
        "created_at": datetime.utcnow()
    }

@pytest.fixture
def mock_customer_data():
    return {
        "name": "Test User",
        "phone": "1234567890",
        "created_at": datetime.utcnow()
    }

@pytest.fixture
def mock_feedback_id():
    return str(ObjectId())

@pytest.fixture
def mock_customer_id():
    return str(ObjectId()) 