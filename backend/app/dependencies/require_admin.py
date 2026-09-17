from fastapi import Header, HTTPException

from app.services import auth_service


def require_admin(authorization: str = Header(default="")) -> dict:
    scheme, _, token = authorization.partition(" ")
    if scheme != "Bearer" or not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        return auth_service.verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")