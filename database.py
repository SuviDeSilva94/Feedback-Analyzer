import os
from pymongo import MongoClient
from bson import ObjectId
import logging
from dotenv import load_dotenv
import certifi
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG level
logger = logging.getLogger(__name__)

# Get MongoDB connection details from environment variables
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "feedback_db")

# Log connection details (without password)
logger.debug(f"MongoDB Cluster: {MONGODB_CLUSTER}")
logger.debug(f"MongoDB Database: {MONGODB_DATABASE}")
logger.debug(f"MongoDB Username: {MONGODB_USERNAME}")

# Construct MongoDB URL
MONGODB_URL = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/{MONGODB_DATABASE}?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Initialize MongoDB client with SSL certificate
    logger.debug("Attempting to connect to MongoDB...")
    client = MongoClient(MONGODB_URL, tlsCAFile=certifi.where())
    # Test the connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    logger.error(f"Connection URL (without password): mongodb+srv://{MONGODB_USERNAME}:****@{MONGODB_CLUSTER}/{MONGODB_DATABASE}")
    raise

db = client[MONGODB_DATABASE]
feedback_collection = db.feedback
customer_collection = db.customers
users_collection = db.users  # Add users collection

# Create indexes
try:
    # Create unique index on email field
    users_collection.create_index("email", unique=True)
    logger.info("Created unique index on email field in users collection")
    
    # Drop existing employee_id index if it exists
    try:
        users_collection.drop_index("employee_id_1")
        logger.info("Dropped existing employee_id index")
    except Exception as e:
        logger.debug(f"No existing employee_id index to drop: {str(e)}")
    
    # Create non-unique index on employee_id field
    users_collection.create_index("employee_id", unique=False)
    logger.info("Created non-unique index on employee_id field in users collection")
except Exception as e:
    logger.error(f"Error creating indexes: {str(e)}")
    raise

def get_or_create_customer(customer_data):
    """Get existing customer or create new one."""
    try:
        # Check if customer exists by phone number
        existing_customer = customer_collection.find_one({"phone": customer_data["phone"]})
        if existing_customer:
            logger.info(f"Found existing customer with ID: {existing_customer['_id']}")
            return str(existing_customer["_id"])
        
        # Create new customer
        customer_data["created_at"] = datetime.utcnow()
        result = customer_collection.insert_one(customer_data)
        logger.info(f"Created new customer with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error in get_or_create_customer: {str(e)}")
        raise

async def store_feedback(feedback_data):
    """Store feedback in MongoDB."""
    try:
        # Handle customer data if provided
        if "customer" in feedback_data:
            customer_id = get_or_create_customer(feedback_data["customer"])
            feedback_data["customer_id"] = customer_id
            del feedback_data["customer"]  # Remove customer data from feedback document
        
        feedback_data["created_at"] = datetime.utcnow()
        result = feedback_collection.insert_one(feedback_data)
        if not result.inserted_id:
            raise Exception("Failed to insert feedback")
        logger.info(f"Stored feedback with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error storing feedback: {str(e)}")
        raise

async def get_feedback(feedback_id):
    """Retrieve feedback by ID."""
    try:
        logger.debug(f"Retrieving feedback with ID: {feedback_id}")
        if not ObjectId.is_valid(feedback_id):
            logger.error(f"Invalid feedback ID format: {feedback_id}")
            raise ValueError(f"Invalid feedback ID format: {feedback_id}")
            
        feedback = feedback_collection.find_one({"_id": ObjectId(feedback_id)})
        if not feedback:
            logger.error(f"Feedback not found with ID: {feedback_id}")
            raise ValueError(f"Feedback not found with ID: {feedback_id}")
            
        # Convert _id to string
        feedback["_id"] = str(feedback["_id"])
        # Convert datetime to ISO format
        feedback["created_at"] = feedback["created_at"].isoformat()
        
        logger.debug(f"Successfully retrieved feedback: {feedback}")
        return feedback
    except Exception as e:
        logger.error(f"Error retrieving feedback: {str(e)}")
        raise

async def list_feedback(skip=0, limit=10, sentiment=None, topic=None):
    """List feedback with optional filtering"""
    try:
        query = {}
        if sentiment:
            query["sentiment"] = sentiment
        if topic:
            query["main_topic"] = topic
            
        cursor = feedback_collection.find(query).skip(skip).limit(limit)
        feedback_list = []
        for doc in cursor:
            # Convert _id to id
            doc["id"] = str(doc.pop("_id"))
            # Convert datetime to ISO format
            doc["created_at"] = doc["created_at"].isoformat()
            feedback_list.append(doc)
            
        logger.info(f"Retrieved {len(feedback_list)} feedback entries")
        return feedback_list
    except Exception as e:
        logger.error(f"Error listing feedback: {str(e)}")
        raise

async def get_feedback_stats():
    """Get feedback statistics"""
    try:
        logger.debug("Counting total feedback...")
        total = feedback_collection.count_documents({})
        logger.debug(f"Total feedback count: {total}")
        
        # Get sentiment distribution
        logger.debug("Calculating sentiment distribution...")
        sentiment_stats = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        try:
            sentiment_pipeline = [
                {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
            ]
            for doc in feedback_collection.aggregate(sentiment_pipeline):
                sentiment_stats[doc["_id"]] = int(doc["count"])
            logger.debug(f"Sentiment distribution: {sentiment_stats}")
        except Exception as e:
            logger.error(f"Error calculating sentiment distribution: {str(e)}")
            # Continue with default sentiment stats
            
        # Get topic distribution
        logger.debug("Calculating topic distribution...")
        topic_stats = {
            "product_quality": 0,
            "customer_service": 0,
            "delivery": 0,
            "pricing": 0,
            "usability": 0
        }
        try:
            topic_pipeline = [
                {"$group": {"_id": "$main_topic", "count": {"$sum": 1}}}
            ]
            for doc in feedback_collection.aggregate(topic_pipeline):
                topic_stats[doc["_id"]] = int(doc["count"])
            logger.debug(f"Topic distribution: {topic_stats}")
        except Exception as e:
            logger.error(f"Error calculating topic distribution: {str(e)}")
            # Continue with default topic stats
            
        # Prepare final stats
        stats = {
            "total_feedback": int(total),
            "sentiment_distribution": sentiment_stats,
            "topic_distribution": topic_stats
        }
        
        logger.info(f"Generated stats: {stats}")
        return stats
    except Exception as e:
        error_msg = f"Error getting feedback statistics: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) 