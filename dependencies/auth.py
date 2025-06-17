from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.token_service import token_service
from services.user_service import UserService
from models.user import UserResponse
import logging

# Set up logging
logger = logging.getLogger(__name__)

security = HTTPBearer()

def get_user_service():
    return UserService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Verify the access token and return the user data."""
    try:
        token = credentials.credentials
        logger.debug(f"Received token: {token[:10]}...")  # Log first 10 chars for security
        
        payload = token_service.verify_token(token)
        logger.debug(f"Token payload: {payload}")
        
        user = await user_service.get_user_by_id(payload.sub)
        logger.debug(f"Found user: {user}")
        
        if not user:
            logger.warning(f"User not found for sub: {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException as e:
        logger.error(f"HTTP Exception in get_current_user: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 