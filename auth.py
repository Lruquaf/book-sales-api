from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import ADMIN_USERS

security = HTTPBearer()


def admin_required(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials

    # Token hangi admin'e aitse onu bul
    admin_id = next(
        (user for user, user_token in ADMIN_USERS.items() if user_token == token), None
    )

    if not admin_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return admin_id  # Burada token yerine admin_id döndürüyoruz
