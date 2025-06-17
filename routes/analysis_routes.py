# from fastapi import APIRouter
# import logging
# from services.feedback_service import feedback_service
# from services.customer_service import customer_service
# from models.feedback_models import FeedbackRequest, FeedbackResponse

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter(
#     prefix="/analyze",
#     tags=["analysis"],
#     responses={404: {"description": "Not found"}},
# )

# @router.post("/feedback", response_model=FeedbackResponse)
# async def analyze_feedback(feedback: FeedbackRequest):
#     """Analyze feedback sentiment and topics, store in MongoDB."""
#     try:
#         # Process customer data
#         # customer_data = await customer_service.process_customer_data(feedback.customer.dict())
        
#         # Analyze and store feedback
#         feedback_data = await feedback_service.analyze_and_store_feedback(
#             feedback.text,
#             customer_data
#         )
        
#         return feedback_data
#     except Exception as e:
#         logger.error(f"Error in analyze_feedback endpoint: {str(e)}")
#         raise 