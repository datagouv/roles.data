from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer()


def decode_proconnect_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return credentials.credentials
