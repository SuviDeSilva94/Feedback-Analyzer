from abc import ABC, abstractmethod
from models.notification_models import NotificationData
from .base_service import BaseService

class NotificationServiceInterface(BaseService):
    """Interface for notification-related operations.
    
    This interface defines methods for sending and processing notifications.
    It inherits from BaseService to ensure consistent error handling.
    """
    
    @abstractmethod
    async def send_negative_feedback_notification(self, feedback_data: NotificationData) -> bool:
        """Send notification for negative feedback.
        
        Args:
            feedback_data: The feedback data to send notification for.
            
        Returns:
            bool: True if notification was queued successfully, False otherwise.
        """
        pass

    @abstractmethod
    async def process_notification_queue(self) -> None:
        """Process the notification queue.
        
        This method processes any pending notifications in the queue.
        """
        pass 