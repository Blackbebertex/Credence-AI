from __future__ import annotations

import os
import datetime
from dataclasses import dataclass
from typing import Callable, Sequence
import jwt
from fastapi import Depends, Header, HTTPException, status

JWT_SECRET_ENV = "JWT_SECRET"
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "http://keycloak:8080/realms/credence-dev"
JWT_AUDIENCE = "credence-api"
ACCESS_TOKEN_LIFETIME = datetime.timedelta(minutes=15)


def _configured_secret() -> str:
    secret = os.getenv(JWT_SECRET_ENV)
    if not secret or len(secret.encode("utf-8")) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        )
    return secret


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    tenant_id: str
    username: str
    roles: tuple[str, ...]
    mfa_verified: bool = True

    def has_role(self, role: str) -> bool:
        return role in self.roles


def create_access_token(
    *,
    user_id: str,
    tenant_id: str,
    username: str,
    roles: Sequence[str],
    mfa_verified: bool = True,
    secret: str | None = None,
) -> str:
    secret = secret or _configured_secret()
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "preferred_username": username,
        "realm_access": {"roles": list(roles)},
        "mfa_verified": mfa_verified,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + ACCESS_TOKEN_LIFETIME,
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def get_current_user(
    authorization: str | None = Header(default=None),
) -> AuthenticatedUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(
            token,
            _configured_secret(),
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={"require": ["sub", "tenant_id", "aud", "iss", "iat", "exp"]},
        )
    except HTTPException:
        raise
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    roles = tuple(payload.get("realm_access", {}).get("roles", []))
    return AuthenticatedUser(
        user_id=payload["sub"],
        tenant_id=payload["tenant_id"],
        username=payload.get("preferred_username", payload["sub"]),
        roles=roles,
        mfa_verified=payload.get("mfa_verified", False),
    )


def require_role(role: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{role}' is required for this action",
            )
        return user

    return dependency
