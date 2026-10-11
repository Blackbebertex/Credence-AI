from __future__ import annotations

import datetime
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse


def create_app(*, dev_token: str | None = None) -> FastAPI:
    app = FastAPI(
        title="CredenceAI-Gov API",
        version="0.1.0",
        description="Government Digital Evidence, Authenticity and Trust Assurance Platform",
    )

    allowed_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    if "*" in allowed_origins:
        raise ValueError("CORS_ALLOWED_ORIGINS must list explicit origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/", include_in_schema=False)
    async def frontend() -> FileResponse:
        return FileResponse(Path(__file__).parent / "static" / "index.html")

    if dev_token is not None:
        @app.get("/api/v1/dev-session", include_in_schema=False)
        async def development_session(request: Request) -> dict[str, str]:
            client_host = request.client.host if request.client else ""
            if client_host not in {"127.0.0.1", "::1", "testclient"}:
                raise HTTPException(status_code=404, detail="Not found")
            return {"access_token": dev_token}

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "type": "https://credence.gov.in/errors/bad-request",
                "title": "Bad Request",
                "status": 400,
                "detail": str(exc),
                "instance": request.url.path,
            },
            media_type="application/problem+json",
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "type": "https://credence.gov.in/errors/forbidden",
                "title": "Forbidden",
                "status": 403,
                "detail": str(exc),
                "instance": request.url.path,
            },
            media_type="application/problem+json",
        )

    @app.get("/health", status_code=status.HTTP_200_OK)
    async def health_check() -> dict[str, str]:
        return {
            "status": "healthy",
            "service": "credence-gov",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "version": "0.1.0",
        }

    from .api import router as api_router
    app.include_router(api_router)

    return app


app = create_app()
