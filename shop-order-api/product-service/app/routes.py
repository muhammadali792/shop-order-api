import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.auth_service_url}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            return response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service unavailable"
            )

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access require"
        )
    return current_user
