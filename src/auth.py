# # src/auth.py
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from typing import Optional

# from .config import settings
# from .models import TokenData

# # Setup OAuth2 with password flow
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Configure JWT
# SECRET_KEY = settings.SECRET_KEY
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# async def get_service_provider_from_token(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         service_provider_id: int = payload.get("service_provider_id")
#         if service_provider_id is None:
#             raise credentials_exception
#         token_data = TokenData(service_provider_id=service_provider_id)
#     except JWTError:
#         raise credentials_exception

#     return token_data.service_provider_id
