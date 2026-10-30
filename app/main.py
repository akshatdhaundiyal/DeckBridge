from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import DeckBridgeError

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="High-performance headless presentation compiler (JSON to OpenXML .pptx)",
)

# CORS middleware for headless microservice access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix="/v1")


@app.get("/health", tags=["system"], summary="Service health check")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.exception_handler(DeckBridgeError)
async def deck_bridge_error_handler(request: Request, exc: DeckBridgeError):
    return JSONResponse(
        status_code=422,
        content={
            "error": exc.code,
            "detail": exc.message,
        },
    )
