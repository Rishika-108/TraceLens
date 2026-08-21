from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new investigator account",
)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    # Check if username or email already exists
    if UserRepository.get_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_in.username}' is already registered.",
        )
    if UserRepository.get_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_in.email}' is already registered.",
        )

    user = UserRepository.create(db, user_in)

    token_payload = {"sub": user.username, "role": user.role}
    access_token = create_access_token(token_payload)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate investigator credentials and obtain JWT access token",
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = UserRepository.authenticate(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = {"sub": user.username, "role": user.role}
    access_token = create_access_token(token_payload)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated investigator profile",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
