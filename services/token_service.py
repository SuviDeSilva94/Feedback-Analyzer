import os
import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class TokenService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # In production, use a secure key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def create_access_token(self, data: dict) -> str:
        """Create a new JWT access token."""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug("Access token created successfully")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating access token")

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug("Token verified successfully")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise HTTPException(status_code=500, detail="Error verifying token")

# Create a singleton instance
token_service = TokenService() 