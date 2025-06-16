import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from typing import Dict
import json
import redis
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NotificationService:
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

    async def send_negative_feedback_notification(self, feedback_data: Dict) -> bool:
        """Queue negative feedback notification for processing."""
        try:
            # Create notification message
            notification = {
                "type": "negative_feedback",
                "feedback_id": feedback_data['id'],
                "customer_name": feedback_data['customer']['name'],
                "customer_phone": feedback_data['customer']['phone'],
                "sentiment_score": feedback_data['sentiment_scores'].get('negative', 0),
                "main_topic": feedback_data['main_topic'],
                "feedback_text": feedback_data['text']
            }

            # Add to Redis queue
            self.redis_client.lpush(self.notification_queue, json.dumps(notification))
            logger.info(f"Queued negative feedback notification for feedback ID: {feedback_data['id']}")
            return True

        except Exception as e:
            logger.error(f"Error queueing notification: {str(e)}")
            return False

    async def process_notification_queue(self):
        """Process notifications from the Redis queue."""
        try:
            while True:
                # Get notification from queue (blocking)
                notification_data = self.redis_client.brpop(self.notification_queue, timeout=0)
                if notification_data:
                    _, notification_json = notification_data
                    notification = json.loads(notification_json)
                    
                    # Create email message
                    msg = MIMEMultipart()
                    msg['From'] = self.smtp_username
                    msg['To'] = self.support_email
                    msg['Subject'] = "⚠️ Negative Feedback Alert"

                    # Create email body
                    body = f"""
                    Negative feedback received that requires attention:

                    Feedback ID: {notification['feedback_id']}
                    Customer: {notification['customer_name']}
                    Phone: {notification['customer_phone']}
                    Sentiment Score: {notification['sentiment_score']:.2f}
                    Main Topic: {notification['main_topic']}

                    Feedback Text:
                    {notification['feedback_text']}

                    Please review and respond promptly.
                    """

                    msg.attach(MIMEText(body, 'plain'))

                    # Send email
                    with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                        server.starttls()
                        server.login(self.smtp_username, self.smtp_password)
                        server.send_message(msg)

                    logger.info(f"Processed notification for feedback ID: {notification['feedback_id']}")

        except Exception as e:
            logger.error(f"Error processing notification queue: {str(e)}")
            # Re-queue the notification if processing fails
            if notification_data:
                self.redis_client.lpush(self.notification_queue, notification_json)

# Create a singleton instance
notification_service = NotificationService() 