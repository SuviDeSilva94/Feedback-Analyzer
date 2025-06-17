from typing import Dict, List, Optional, Any
from datetime import datetime
from database import store_feedback, get_feedback, list_feedback, get_feedback_stats, db
from sentiment_analyzer import SentimentAnalyzer
from topic_classifier import TopicClassifier
from ai_topic_classifier import ai_topic_classifier
from interfaces.feedback_service_interface import FeedbackServiceInterface
import traceback
from services.notification_service import notification_service
from models.feedback_models import FeedbackRequest, FeedbackResponse
from ai_sentiment_analyzer import AISentimentAnalyzer
import logging
from fastapi import HTTPException
from bson import ObjectId

# Set up logging
logger = logging.getLogger(__name__)

class FeedbackService(FeedbackServiceInterface):
    def __init__(self):
        self.db = db
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ai_sentiment_analyzer = AISentimentAnalyzer()
        self.topic_classifier = TopicClassifier()

    # async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """Validate feedback data."""
    #     # This method is required by BaseService but not used in this service
    #     # Validation is handled by Pydantic models
    #     return data

    # async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """Process feedback data."""
    #     # This method is required by BaseService but not used in this service
    #     # Processing is handled by analyze_and_store_feedback and analyze_and_store_feedback_ai
    #     return data

    async def analyze_and_store_feedback(self, text: str, customer_data: Dict) -> Dict:
        """Analyze feedback and store in database."""
        try:
            # Get sentiment analysis results
            sentiment = self.sentiment_analyzer.get_sentiment(text)
            sentiment_scores = self.sentiment_analyzer.analyze(text)
            
            # Get topic analysis results using AI classifier
            main_topic = await ai_topic_classifier.get_main_topic(text)
            topic_scores = await ai_topic_classifier.classify(text)
            top_topics = await ai_topic_classifier.get_top_topics(text)
            
            # Prepare feedback data
            feedback_data = {
                "text": text,
                "customer": customer_data,
                "sentiment": sentiment,
                "sentiment_scores": sentiment_scores,
                "main_topic": main_topic,
                "topic_scores": topic_scores,
                "top_topics": top_topics,
                "created_at": datetime.utcnow()
            }
            
            # Store in MongoDB
            feedback_id = await store_feedback(feedback_data)
            if not feedback_id:
                raise Exception("Failed to store feedback in database")
            
            # Convert ObjectId to string and add to response
            feedback_data["id"] = str(feedback_id)
            
            # Convert datetime to ISO format string
            feedback_data["created_at"] = feedback_data["created_at"].isoformat()
            
            # Check if sentiment is negative and send notification
            if sentiment == "negative":
                await notification_service.send_negative_feedback_notification(feedback_data)
            
            return feedback_data
        except Exception as e:
            logger.error(f"Error in analyze_and_store_feedback: {str(e)}")
            await self.handle_error(e)
            raise

    async def analyze_and_store_feedback_ai(self, feedback_data: Dict) -> Dict:
        """Analyze feedback and store in database using AI sentiment analysis."""
        try:
            text = feedback_data.get('feedbackText', '')
            customer_data = feedback_data.get('customer', {})
            
            logger.info(f"Starting AI analysis for text: {text}")
            
            # Get sentiment analysis using AI
            sentiment = self.ai_sentiment_analyzer.get_sentiment(text)
            sentiment_scores = self.ai_sentiment_analyzer.analyze(text)
            
            logger.info("Got sentiment analysis results")
            
            # Get topic analysis results using AI classifier
            logger.info("Starting topic classification")
            topic_scores = await ai_topic_classifier.classify(text)
            logger.info(f"Got topic scores: {topic_scores}")
            
            main_topic = await ai_topic_classifier.get_main_topic(text)
            logger.info(f"Got main topic: {main_topic}")
            
            top_topics = await ai_topic_classifier.get_top_topics(text)
            logger.info(f"Got top topics: {top_topics}")

            # Prepare feedback data
            feedback_doc = {
                "text": text,
                "customer": customer_data,
                "sentiment": sentiment,
                "sentiment_scores": sentiment_scores,
                "main_topic": main_topic,
                "topic_scores": topic_scores,
                "top_topics": top_topics,
                "created_at": datetime.utcnow()
            }

            logger.info(f"Prepared feedback document: {feedback_doc}")

            # Store in MongoDB
            feedback_id = await store_feedback(feedback_doc)
            if not feedback_id:
                raise Exception("Failed to store feedback in database")
            
            # Convert ObjectId to string and add to response
            feedback_doc["id"] = str(feedback_id)
            
            # Convert datetime to ISO format string
            feedback_doc["created_at"] = feedback_doc["created_at"].isoformat()
            
            # Check if sentiment is negative and send notification
            if sentiment == "negative":
                await notification_service.send_negative_feedback_notification(feedback_doc)
            
            logger.info(f"Successfully stored and analyzed feedback with ID: {feedback_id}")
            return feedback_doc

        except Exception as e:
            logger.error(f"Error in analyze_and_store_feedback_ai: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            await self.handle_error(e)
            raise

    async def list_all_feedback(
        self,
        skip: int = 0,
        limit: int = 10,
        sentiment: Optional[str] = None,
        topic: Optional[str] = None
    ) -> List[Dict]:
        """List feedback with optional filtering."""
        try:
            # Validate filters
            if sentiment and not await self.validate_sentiment(sentiment):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid sentiment filter. Must be one of: positive, negative, neutral"
                )
            
            if topic and not await self.validate_topic(topic):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid topic filter. Must be one of: {', '.join(self.get_valid_topics())}"
                )
            
            feedback_list = await list_feedback(skip=skip, limit=limit, sentiment=sentiment, topic=topic)
            if not feedback_list:
                return []
            return feedback_list
        except Exception as e:
            logger.error(f"Error in list_all_feedback: {str(e)}")
            await self.handle_error(e)
            raise

    async def get_feedback_by_id(self, feedback_id: str) -> Dict:
        """Get feedback by ID."""
        try:
            logger.debug(f"Getting feedback by ID: {feedback_id}")
            if not ObjectId.is_valid(feedback_id):
                logger.error(f"Invalid feedback ID format: {feedback_id}")
                raise HTTPException(status_code=400, detail="Invalid feedback ID format")
            
            feedback = await get_feedback(feedback_id)
            if not feedback:
                logger.error(f"Feedback not found with ID: {feedback_id}")
                raise HTTPException(status_code=404, detail=f"Feedback not found with ID: {feedback_id}")
            
            logger.debug(f"Successfully retrieved feedback: {feedback}")
            return feedback
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_feedback_by_id: {str(e)}")
            await self.handle_error(e)
            raise

    async def get_stats(self) -> Dict:
        """Get feedback statistics."""
        try:
            logger.debug("Fetching feedback statistics...")
            stats = await get_feedback_stats()
            if not stats:
                logger.warning("No feedback statistics found, returning empty stats")
                return {
                    "total_feedback": 0,
                    "sentiment_distribution": {
                        "positive": 0,
                        "negative": 0,
                        "neutral": 0
                    },
                    "topic_distribution": {
                        "product_quality": 0,
                        "customer_service": 0,
                        "delivery": 0,
                        "pricing": 0,
                        "usability": 0
                    }
                }
            
            logger.debug(f"Retrieved stats: {stats}")
            return stats
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_stats: {str(e)}")
            await self.handle_error(e)
            raise

    async def validate_sentiment(self, sentiment: str) -> bool:
        """Validate sentiment value."""
        valid_sentiments = ["positive", "negative", "neutral"]
        return sentiment.lower() in valid_sentiments

    async def validate_topic(self, topic: str) -> bool:
        """Validate topic value."""
        return topic in self.get_valid_topics()

    def get_valid_topics(self) -> List[str]:
        """Get list of valid topics."""
        return [
            "product_quality",
            "customer_service",
            "delivery",
            "pricing",
            "usability"
        ]

    async def handle_error(self, error: Exception) -> None:
        """Handle errors in feedback processing."""
        error_message = str(error)
        logger.error(f"Error details: {error_message}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_message}")

# Create a singleton instance
feedback_service = FeedbackService() 