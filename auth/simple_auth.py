from fastapi import HTTPException, status, Request
from typing import Optional
import uuid


def get_current_user_id(request: Request) -> str:
    user_id = request.cookies.get("user_id") or request.query_params.get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())[:8]

    return user_id


def require_admin(request: Request):
    admin_token = request.cookies.get("admin_token") or request.query_params.get("admin_token")

    if admin_token != "admin123":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора. Используйте admin_token=admin123"
        )

    return True