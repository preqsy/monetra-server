from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import firebase_admin
from firebase_admin import auth
from .firebase_init import init_firebase

security = HTTPBearer(auto_error=False)
firebase_app = init_firebase()


def verify_firebase_token(
    creds: HTTPAuthorizationCredentials = Depends(security),
    check_revoked: bool = False,
):
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = creds.credentials
    try:
        decoded = auth.verify_id_token(
            token, app=firebase_app, check_revoked=check_revoked
        )
        # decoded contains uid, email, etc.
        return decoded
    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase ID token",
        )
