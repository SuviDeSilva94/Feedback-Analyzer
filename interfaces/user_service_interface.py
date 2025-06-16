from abc import ABC, abstractmethod
from typing import Optional
from models.user import UserCreate, UserResponse, UserLogin

class UserServiceInterface(ABC):
    @abstractmethod
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        pass

    @abstractmethod
    def validate_email(self, email: str) -> bool:
        """Validate email format and uniqueness."""
        pass

    @abstractmethod
    def validate_password(self, password: str) -> bool:
        """Validate password strength."""
        pass

    @abstractmethod
    def authenticate_user(self, login_data: UserLogin) -> Optional[UserResponse]:
        """Authenticate user with email and password."""
        pass 