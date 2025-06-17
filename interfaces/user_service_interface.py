from abc import ABC, abstractmethod
from typing import Optional, Tuple
from models.user import UserCreate, UserResponse, UserLogin
from .base_service import BaseService

class UserServiceInterface(BaseService):
    """Interface for user-related operations.
    
    This interface defines methods for user management, including creation,
    authentication, and validation. It inherits from BaseService to ensure
    consistent error handling.
    """
    
    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user.
        
        Args:
            user_data: The user data for creation.
            
        Returns:
            UserResponse: The created user's data.
        """
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email.
        
        Args:
            email: The email address to search for.
            
        Returns:
            Optional[UserResponse]: The user data if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID.
        
        Args:
            user_id: The user ID to search for.
            
        Returns:
            Optional[UserResponse]: The user data if found, None otherwise.
        """
        pass

    @abstractmethod
    async def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email format and uniqueness.
        
        Args:
            email: The email address to validate.
            
        Returns:
            Tuple[bool, str]: A tuple containing (is_valid, error_message).
        """
        pass

    @abstractmethod
    def validate_password(self, password: str) -> bool:
        """Validate password strength.
        
        Args:
            password: The password to validate.
            
        Returns:
            bool: True if the password meets strength requirements, False otherwise.
        """
        pass

    @abstractmethod
    async def authenticate_user(self, login_data: UserLogin) -> Tuple[UserResponse, str]:
        """Authenticate user with email and password.
        
        Args:
            login_data: The login credentials.
            
        Returns:
            Tuple[UserResponse, str]: A tuple containing (user_data, access_token).
        """
        pass 