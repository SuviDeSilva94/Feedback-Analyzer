from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging
import traceback
from services.feedback_service import FeedbackService
from services.customer_service import CustomerService
from models.feedback_models import FeedbackRequest, FeedbackResponse, FeedbackStats
from dependencies.auth import get_current_user
from models.user import UserResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)

def get_feedback_service():
    return FeedbackService()

def get_customer_service():
    return CustomerService()

@router.post("/submit-and-analyze-feedback", response_model=FeedbackResponse)
async def analyze_feedback(
    feedback: FeedbackRequest,
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Submit and analyze feedback - Public endpoint"""
    try:
        result = await feedback_service.analyze_and_store_feedback(
            text=feedback.feedback_text,
            customer_data=feedback.customer.dict()
        )
        return result
    except Exception as e:
        error_msg = f"Error in analyze_feedback endpoint: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-and-analyze-feedback-ai", response_model=FeedbackResponse)
async def analyze_feedback_ai(
    feedback: FeedbackRequest,
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Submit and analyze feedback using AI sentiment analysis - Public endpoint"""
    try:
        result = await feedback_service.analyze_and_store_feedback_ai(feedback)
        return result
    except Exception as e:
        error_msg = f"Error in analyze_feedback_ai endpoint: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[FeedbackResponse])
async def list_all_feedback(
    skip: int = 0,
    limit: int = 10,
    sentiment: Optional[str] = None,
    topic: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """List all feedback with optional filtering - Protected endpoint"""
    try:
        feedback_list = await feedback_service.list_all_feedback(skip, limit, sentiment, topic)
        return feedback_list
    except Exception as e:
        error_msg = f"Error in list_all_feedback endpoint: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=FeedbackStats)
async def get_stats(
    current_user: UserResponse = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Get feedback statistics - Protected endpoint"""
    try:
        logger.debug("Calling get_stats endpoint")
        stats = await feedback_service.get_stats()
        logger.debug(f"Stats response: {stats}")
        return stats
    except Exception as e:
        error_msg = f"Error in get_stats endpoint: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_by_id(
    feedback_id: str,
    current_user: UserResponse = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Get feedback by ID - Protected endpoint"""
    try:
        return await feedback_service.get_feedback_by_id(feedback_id)
    except HTTPException as he:
        # Re-raise HTTP exceptions directly
        raise he
    except Exception as e:
        error_msg = f"Error in get_feedback_by_id endpoint: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e)) 