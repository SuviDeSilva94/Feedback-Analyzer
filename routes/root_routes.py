from fastapi import APIRouter

router = APIRouter(
    tags=["root"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def root():
    """API information and available endpoints."""
    return {
        "name": "Feedback Analysis System",
        "version": "1.0.0",
        "endpoints": {
            "/analyze/feedback": "POST - Analyze feedback sentiment and topics",
            "/feedback/{feedback_id}": "GET - Get feedback by ID",
            "/feedback": "GET - List feedback with optional filtering",
            "/feedback/stats": "GET - Get feedback statistics"
        }
    } 