from fastapi import FastAPI
import logging
from routes import feedback_routes, analysis_routes, root_routes, user_routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Feedback Analysis System",
    description="A system for analyzing customer feedback using sentiment analysis and topic classification",
    version="1.0.0"
)

# Include routers
app.include_router(root_routes.router)
app.include_router(feedback_routes.router)
app.include_router(analysis_routes.router)
app.include_router(user_routes.router) 