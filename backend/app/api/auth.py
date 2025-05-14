from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..core.database import get_db
from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT settings
SECRET_KEY = "your-secret-key"  # TODO: Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    """Create a new JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get access token for user.
    """
    try:
        # TODO: Implement actual user authentication
        # For now, just return a dummy token
        access_token = create_access_token({"sub": "user@example.com"})
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register")
async def register(
    user_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Register a new user.
    """
    try:
        # TODO: Implement user registration
        return {
            "status": "success",
            "message": "User registered successfully"
        }
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user information.
    """
    try:
        # TODO: Implement user retrieval
        return {
            "email": "user@example.com",
            "is_active": True
        }
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 