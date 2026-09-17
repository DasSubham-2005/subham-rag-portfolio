from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

bearer = HTTPBearer(auto_error=False)

def login(username: str, password: str):
    if username != settings.admin_username or password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = jwt.encode({"sub": username, "exp": datetime.now(timezone.utc) + timedelta(hours=12)}, settings.secret_key, algorithm="HS256")
    return token

def require_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin login required")
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        if payload.get("sub") != settings.admin_username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
