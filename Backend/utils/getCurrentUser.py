from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        return payload  # this contains user_role, user_id, etc.
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
