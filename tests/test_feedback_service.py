import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from feedback_analyzer.interfaces.feedback_service_interface import FeedbackServiceInterface
from feedback_analyzer.services.feedback_service import FeedbackService

class TestFeedbackService:
    @pytest.fixture
    def feedback_service(self):
        return FeedbackService()

    @pytest.fixture
    def mock_sentiment_analyzer(self):
        with patch('services.feedback_service.SentimentAnalyzer') as mock:
            mock_instance = Mock()
            mock_instance.get_sentiment.return_value = "positive"
            mock_instance.analyze.return_value = {"positive": 0.8, "negative": 0.2}
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_topic_classifier(self):
        with patch('services.feedback_service.TopicClassifier') as mock:
            mock_instance = Mock()
            mock_instance.get_main_topic.return_value = "product_quality"
            mock_instance.classify.return_value = {
                "product_quality": 0.6,
                "customer_service": 0.2,
                "delivery": 0.1,
                "pricing": 0.05,
                "usability": 0.05
            }
            mock_instance.get_top_topics.return_value = ["product_quality", "customer_service"]
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_database(self):
        with patch('services.feedback_service.store_feedback') as mock_store, \
             patch('services.feedback_service.get_feedback') as mock_get, \
             patch('services.feedback_service.list_feedback') as mock_list, \
             patch('services.feedback_service.get_feedback_stats') as mock_stats:
            
            mock_store.return_value = "test_feedback_id"
            mock_get.return_value = {
                "_id": ObjectId("test_feedback_id"),
                "text": "Great product!",
                "sentiment": "positive",
                "main_topic": "product_quality"
            }
            mock_list.return_value = [{
                "_id": ObjectId("test_feedback_id"),
                "text": "Great product!",
                "sentiment": "positive",
                "main_topic": "product_quality"
            }]
            mock_stats.return_value = {
                "total_feedback": 1,
                "sentiment_distribution": {"positive": 1},
                "topic_distribution": {"product_quality": 1}
            }
            yield {
                "store": mock_store,
                "get": mock_get,
                "list": mock_list,
                "stats": mock_stats
            }

    @pytest.mark.asyncio
    async def test_validate_valid_data(self, feedback_service):
        data = {
            "text": "Great product!",
            "customer": {"name": "Test User", "phone": "1234567890"}
        }
        result = await feedback_service.validate(data)
        assert result == data

    @pytest.mark.asyncio
    async def test_validate_empty_text(self, feedback_service):
        data = {
            "text": "",
            "customer": {"name": "Test User", "phone": "1234567890"}
        }
        with pytest.raises(HTTPException) as exc_info:
            await feedback_service.validate(data)
        assert exc_info.value.status_code == 400
        assert "Feedback text is required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_long_text(self, feedback_service):
        data = {
            "text": "x" * 1001,
            "customer": {"name": "Test User", "phone": "1234567890"}
        }
        with pytest.raises(HTTPException) as exc_info:
            await feedback_service.validate(data)
        assert exc_info.value.status_code == 400
        assert "Feedback text cannot exceed 1000 characters" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_analyze_and_store_feedback(
        self, 
        feedback_service, 
        mock_sentiment_analyzer, 
        mock_topic_classifier, 
        mock_database
    ):
        text = "Great product!"
        customer_data = {"name": "Test User", "phone": "1234567890"}
        
        result = await feedback_service.analyze_and_store_feedback(text, customer_data)
        
        assert result["id"] == "test_feedback_id"
        assert result["text"] == text
        assert result["sentiment"] == "positive"
        assert result["main_topic"] == "product_quality"
        assert "sentiment_scores" in result
        assert "topic_scores" in result
        assert "top_topics" in result
        assert "created_at" in result

    @pytest.mark.asyncio
    async def test_get_feedback_by_id(self, feedback_service, mock_database):
        result = await feedback_service.get_feedback_by_id("test_feedback_id")
        assert result["id"] == "test_feedback_id"
        assert result["text"] == "Great product!"
        assert result["sentiment"] == "positive"
        assert result["main_topic"] == "product_quality"

    @pytest.mark.asyncio
    async def test_get_feedback_by_invalid_id(self, feedback_service):
        with pytest.raises(HTTPException) as exc_info:
            await feedback_service.get_feedback_by_id("invalid_id")
        assert exc_info.value.status_code == 400
        assert "Invalid feedback ID format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_list_all_feedback(self, feedback_service, mock_database):
        result = await feedback_service.list_all_feedback()
        assert len(result) == 1
        assert result[0]["id"] == "test_feedback_id"
        assert result[0]["text"] == "Great product!"

    @pytest.mark.asyncio
    async def test_list_feedback_with_filters(self, feedback_service, mock_database):
        result = await feedback_service.list_all_feedback(
            sentiment="positive",
            topic="product_quality"
        )
        assert len(result) == 1
        assert result[0]["sentiment"] == "positive"
        assert result[0]["main_topic"] == "product_quality"

    @pytest.mark.asyncio
    async def test_get_stats(self, feedback_service, mock_database):
        result = await feedback_service.get_stats()
        assert result["total_feedback"] == 1
        assert result["sentiment_distribution"]["positive"] == 1
        assert result["topic_distribution"]["product_quality"] == 1

    @pytest.mark.asyncio
    async def test_validate_sentiment(self, feedback_service):
        assert await feedback_service.validate_sentiment("positive") is True
        assert await feedback_service.validate_sentiment("negative") is True
        assert await feedback_service.validate_sentiment("neutral") is True
        assert await feedback_service.validate_sentiment("invalid") is False

    @pytest.mark.asyncio
    async def test_validate_topic(self, feedback_service):
        assert await feedback_service.validate_topic("product_quality") is True
        assert await feedback_service.validate_topic("customer_service") is True
        assert await feedback_service.validate_topic("invalid") is False 