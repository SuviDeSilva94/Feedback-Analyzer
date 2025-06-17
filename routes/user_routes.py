from fastapi import APIRouter, Depends, HTTPException
from models.user import UserCreate, UserResponse, UserLogin
from services.user_service import UserService
from pymongo.errors import DuplicateKeyError

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

def get_user_service():
    return UserService()

@router.post("/signup", response_model=UserResponse)
async def signup(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Create a new user account.
    
    - **email**: User's email address (must be unique)
    - **full_name**: User's full name
    - **phone**: User's phone number
    - **password**: User's password (min 8 chars, must contain uppercase, lowercase, and number)
    """
    try:
        return await user_service.create_user(user_data)
    except HTTPException:
        # Re-raise HTTP exceptions directly to preserve status code and detail
        raise
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """Login user and return user data with access token."""
    try:
        user, access_token = await user_service.authenticate_user(login_data)
        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 