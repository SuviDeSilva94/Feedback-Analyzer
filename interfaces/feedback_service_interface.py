from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .base_service import BaseService

class FeedbackServiceInterface(BaseService):
    """Interface for feedback-related operations."""
    
    @abstractmethod
    async def analyze_and_store_feedback(self, text: str, customer_data: Dict) -> Dict:
        """Analyze feedback and store in database."""
        pass

    @abstractmethod
    async def analyze_and_store_feedback_ai(self, feedback_data: Dict) -> Dict:
        """Analyze feedback and store in database using AI sentiment analysis."""
        pass

    @abstractmethod
    async def get_feedback_by_id(self, feedback_id: str) -> Dict:
        """Get feedback by ID."""
        pass

    @abstractmethod
    async def list_all_feedback(
        self,
        skip: int = 0,
        limit: int = 10,
        sentiment: Optional[str] = None,
        topic: Optional[str] = None
    ) -> List[Dict]:
        """List feedback with optional filtering."""
        pass

    @abstractmethod
    async def get_stats(self) -> Dict:
        """Get feedback statistics."""
        pass

    @abstractmethod
    async def validate_sentiment(self, sentiment: str) -> bool:
        """Validate sentiment value."""
        pass

    @abstractmethod
    async def validate_topic(self, topic: str) -> bool:
        """Validate topic value."""
        pass 