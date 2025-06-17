from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.token import TokenPayload
from .base_service import BaseService

class TokenServiceInterface(BaseService):
    """Interface for token-related operations.
    
    This interface defines methods for creating and verifying JWT tokens.
    It inherits from BaseService to ensure consistent error handling.
    """
    
    @abstractmethod
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a new JWT access token.
        
        Args:
            data: Dictionary containing the data to be encoded in the token.
            
        Returns:
            str: The encoded JWT token.
        """
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verify and decode a JWT token.
        
        Args:
            token: The JWT token to verify.
            
        Returns:
            Optional[TokenPayload]: The decoded token payload if valid, None otherwise.
        """
        pass 