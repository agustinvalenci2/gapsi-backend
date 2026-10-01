from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import Token, UserRead, UserRegister
from app.services.user_service import UserAlreadyExistsError, UserService
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister):
    try:
        return await UserService.register(data)
    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if len(form.password) > 128 or len(form.username) > 100:
        user = None
    else:
        user = await UserService.authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Wrong user/password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(user.id),
        expires_in=get_settings().access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user
