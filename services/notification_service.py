import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from typing import Dict
import json
import redis
from dotenv import load_dotenv
from models.notification_models import NotificationData
from interfaces.notification_service_interface import NotificationServiceInterface
from fastapi import HTTPException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NotificationService(NotificationServiceInterface):
    def __init__(self):
        """Initialize notification service with SMTP and Redis settings."""
        # SMTP settings
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.support_email = os.getenv("SUPPORT_EMAIL", "support@example.com")

        # Redis settings
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            decode_responses=True
        )
        self.notification_queue = "notification_queue"

    async def handle_error(self, error: Exception) -> None:
        """Handle service errors in a consistent way.
        
        Args:
            error: The exception that occurred during service operation.
        """
        logger.error(f"Notification service error: {str(error)}")
        if isinstance(error, redis.RedisError):
            raise HTTPException(status_code=503, detail="Notification service temporarily unavailable")
        elif isinstance(error, smtplib.SMTPException):
            raise HTTPException(status_code=503, detail="Email service temporarily unavailable")
        else:
            raise HTTPException(status_code=500, detail="Error processing notification")

    async def send_negative_feedback_notification(self, feedback_data: NotificationData) -> bool:
        """Queue negative feedback notification for processing."""
        try:
            notification = feedback_data.dict()
            self.redis_client.lpush(self.notification_queue, json.dumps(notification))
            logger.info(f"Queued negative feedback notification for feedback ID: {feedback_data.feedback_id}")
            return True
        except Exception as e:
            logger.error(f"Error queueing notification: {str(e)}")
            await self.handle_error(e)
            return False

    async def process_notification_queue(self) -> None:
        """Process the notification queue."""
        try:
            while True:
                notification_data = self.redis_client.rpop(self.notification_queue)
                if not notification_data:
                    break
                
                notification = json.loads(notification_data)
                await self._send_email_notification(notification)
                logger.info(f"Processed notification for feedback ID: {notification.get('feedback_id')}")
        except Exception as e:
            logger.error(f"Error processing notification queue: {str(e)}")
            await self.handle_error(e)

    async def _send_email_notification(self, notification: Dict) -> None:
        """Send email notification for negative feedback."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.support_email
            msg['Subject'] = "Negative Feedback Alert"

            body = f"""
            Negative feedback received:
            
            Feedback ID: {notification.get('feedback_id')}
            Customer: {notification.get('customer_name')}
            Feedback: {notification.get('feedback_text')}
            Sentiment: {notification.get('sentiment')}
            Topic: {notification.get('topic')}
            """

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email notification sent for feedback ID: {notification.get('feedback_id')}")
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            await self.handle_error(e)

# Create a singleton instance
notification_service = NotificationService() 