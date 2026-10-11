import uuid
from fastapi import status, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.security import decode_access_token
from jose import JWTError
from sqlalchemy import select

bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized()->HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid or missing authetication token",
        headers={"WWW-Authenticate":"Bearer"}
    )

async def get_current_user(credentials:HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
                   db:AsyncSession = Depends(get_db))->User:
    if credentials is None:
        raise unauthorized()
    try:
        payload = decode_access_token(credentials)
        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tenant_id"])
    except (JWTError, KeyError, ValueError, TypeError):
        raise unauthorized()

    user = await db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None or user.tenant_id != tenant_id:
        raise unauthorized()

    return user

async def get_tenant_id(user:User = Depends(get_current_user))->uuid.UUID:
    return user.tenant_id