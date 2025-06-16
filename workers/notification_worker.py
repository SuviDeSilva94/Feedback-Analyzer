import asyncio
import logging
from services.notification_service import notification_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_notification_worker():
    """Run the notification queue processor."""
    logger.info("Starting notification worker...")
    try:
        await notification_service.process_notification_queue()
    except Exception as e:
        logger.error(f"Error in notification worker: {str(e)}")
        # Restart the worker after a delay
        await asyncio.sleep(5)
        await run_notification_worker()

if __name__ == "__main__":
    asyncio.run(run_notification_worker()) 