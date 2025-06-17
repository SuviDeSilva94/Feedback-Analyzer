import os
import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException
from interfaces.token_service_interface import TokenServiceInterface
from models.token import TokenPayload

logger = logging.getLogger(__name__)

class TokenService(TokenServiceInterface):
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # In production, use a secure key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        logger.debug(f"TokenService initialized with algorithm: {self.algorithm}")

    async def handle_error(self, error: Exception) -> None:
        """Handle service errors in a consistent way.
        
        Args:
            error: The exception that occurred during service operation.
        """
        logger.error(f"Token service error: {str(error)}")
        if isinstance(error, jwt.ExpiredSignatureError):
            raise HTTPException(status_code=401, detail="Token has expired")
        elif isinstance(error, (jwt.InvalidTokenError, jwt.PyJWTError)):
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            raise HTTPException(status_code=500, detail="Error processing token")

    def create_access_token(self, data: dict) -> str:
        """Create a new JWT access token."""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({
                "exp": expire,
                "type": "access"  # Add the required type field
            })
            logger.debug(f"Creating token with data: {to_encode}")
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug("Access token created successfully")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating access token")

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verify and decode a JWT token."""
        try:
            logger.debug(f"Verifying token with secret key: {self.secret_key[:5]}...")
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug(f"Token payload: {payload}")
            
            # Convert datetime strings to datetime objects if needed
            if 'exp' in payload and isinstance(payload['exp'], (int, float)):
                payload['exp'] = datetime.fromtimestamp(payload['exp'])
            if 'iat' in payload and isinstance(payload['iat'], (int, float)):
                payload['iat'] = datetime.fromtimestamp(payload['iat'])
            if 'nbf' in payload and isinstance(payload['nbf'], (int, float)):
                payload['nbf'] = datetime.fromtimestamp(payload['nbf'])
            
            # Ensure type field is present
            if 'type' not in payload:
                payload['type'] = 'access'  # Default to access token if not specified
            
            token_payload = TokenPayload(**payload)
            logger.debug("Token verified successfully")
            return token_payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except (jwt.InvalidTokenError, jwt.PyJWTError) as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error verifying token")


# Create a singleton instance
token_service = TokenService() 