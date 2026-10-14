from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models.models import User, Tenant
from sqlalchemy import select
import secrets
from app.core.security import hash_password, verify_password, create_access_token
from sqlalchemy.exc import IntegrityError
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data:RegisterRequest, db:AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            existing_user = await db.scalar(select(User).where(User.email == str(data.email)))
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists"
                )
            tenant = Tenant(
                name=data.tenant_name,
                api_key = secrets.token_urlsafe(32)
            )

            db.add(tenant)
            await db.flush()

            user = User(
                name=data.name,
                email=str(data.email),
                password_hash=hash_password(data.password),
                tenant_id = tenant.id
            )

            db.add(user)
            await db.flush()
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

@router.post("/login", response_model=TokenResponse)
async def login(data:LoginRequest, db:AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == str(data.email)))
    if (user is None or not user.password_hash or not verify_password(data.password, user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate":"Bearer"}
        )

    token = create_access_token(user_id=str(user.id), tenant_id=str(user.tenant_id))

    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user:User = Depends(get_current_user)):
    return current_user