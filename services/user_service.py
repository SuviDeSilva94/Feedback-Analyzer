import logging
from datetime import datetime
from typing import Optional, Tuple
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from interfaces.user_service_interface import UserServiceInterface
from models.user import UserCreate, UserResponse, UserLogin
from database import db, users_collection
from services.token_service import token_service

logger = logging.getLogger(__name__)

class UserService(UserServiceInterface):
    def __init__(self):
        self.collection = users_collection
        logger.debug("UserService initialized with users collection")
        # Create unique index on email
        self.collection.create_index("email", unique=True)

    def validate_email(self, email: str) -> tuple[bool, str]:
        """Validate email format and check if it exists.
        Returns a tuple of (is_valid, error_message)"""
        try:
            # Validate email format with check_deliverability=False to allow test domains
            validation = validate_email(email, check_deliverability=False)
            email = validation.email  # Get normalized email
            logger.debug(f"Email format validated: {email}")
            
            # Check if email exists
            existing_user = self.collection.find_one({"email": email})
            if existing_user:
                logger.warning(f"Email already exists: {email}")
                return False, "Email already registered"
                
            return True, ""
        except EmailNotValidError as e:
            logger.warning(f"Invalid email format: {str(e)}")
            return False, f"Invalid email format: {str(e)}"
        except Exception as e:
            logger.error(f"Error validating email: {str(e)}")
            return False, f"Error validating email: {str(e)}"

    def validate_password(self, password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            logger.warning("Password too short")
            return False
        if not any(c.isupper() for c in password):
            logger.warning("Password missing uppercase letter")
            return False
        if not any(c.islower() for c in password):
            logger.warning("Password missing lowercase letter")
            return False
        if not any(c.isdigit() for c in password):
            logger.warning("Password missing digit")
            return False
        return True

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            logger.debug(f"Attempting to create user with email: {user_data.email}")
            
            # Validate email and password
            is_valid_email, email_error = self.validate_email(user_data.email)
            if not is_valid_email:
                logger.warning(f"Email validation failed: {email_error}")
                raise HTTPException(status_code=400, detail=email_error)
            
            if not self.validate_password(user_data.password):
                logger.warning("Password does not meet requirements")
                raise HTTPException(status_code=400, detail="Password does not meet requirements")

            # Hash password
            hashed_password = generate_password_hash(user_data.password)
            logger.debug("Password hashed successfully")

            # Create user document
            user_doc = {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "phone": user_data.phone,
                "password": hashed_password,
                "created_at": datetime.utcnow(),
                "employee_id": None  # Explicitly set employee_id to None
            }
            logger.debug("User document created")

            # Insert into database
            result = self.collection.insert_one(user_doc)
            logger.info(f"User created successfully with ID: {result.inserted_id}")
            
            # Return user response
            return UserResponse(
                id=str(result.inserted_id),
                email=user_data.email,
                full_name=user_data.full_name,
                phone=user_data.phone,
                created_at=user_doc["created_at"]
            )

        except DuplicateKeyError:
            logger.warning("Email already registered")
            raise HTTPException(status_code=400, detail="Email already registered")
        except HTTPException:
            # Re-raise HTTP exceptions without logging as error
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating user: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        try:
            user = self.collection.find_one({"email": email})
            if user:
                return UserResponse(
                    id=str(user["_id"]),
                    email=user["email"],
                    full_name=user["full_name"],
                    phone=user["phone"],
                    created_at=user["created_at"]
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            from bson import ObjectId
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return UserResponse(
                    id=str(user["_id"]),
                    email=user["email"],
                    full_name=user["full_name"],
                    phone=user["phone"],
                    created_at=user["created_at"]
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def authenticate_user(self, login_data: UserLogin) -> Tuple[UserResponse, str]:
        """Authenticate user and return user data with access token."""
        try:
            user = self.collection.find_one({"email": login_data.email})
            if not user:
                logger.warning(f"User not found: {login_data.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            if not check_password_hash(user["password"], login_data.password):
                logger.warning(f"Invalid password for user: {login_data.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Create user response
            user_response = UserResponse(
                id=str(user["_id"]),
                email=user["email"],
                full_name=user["full_name"],
                phone=user["phone"],
                created_at=user["created_at"]
            )

            # Generate access token
            token_data = {
                "sub": str(user["_id"]),
                "email": user["email"],
                "full_name": user["full_name"]
            }
            access_token = token_service.create_access_token(token_data)
            
            return user_response, access_token

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Export the UserService class
__all__ = ['UserService'] 