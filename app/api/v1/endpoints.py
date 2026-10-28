import re
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.engine.compiler import compiler
from app.schemas.deck import DeckPayload

router = APIRouter(prefix="/decks", tags=["decks"])


def sanitize_filename(title: str) -> str:
    """Create a safe ASCII filename for Content-Disposition header."""
    clean = re.sub(r"[^a-zA-Z0-9_\- ]", "", title).strip()
    safe = clean.replace(" ", "_")
    return f"{safe}.pptx" if safe else "presentation.pptx"


@router.post(
    "/compile",
    summary="Compile declarative JSON slide payload into OpenXML .pptx presentation",
    response_description="Binary OpenXML .pptx presentation file stream",
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": {}
            },
            "description": "Streamed .pptx presentation binary",
        }
    },
)
async def compile_deck(payload: DeckPayload):
    buffer = compiler.compile(payload)
    filename = sanitize_filename(payload.title)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/validate", summary="Validate deck payload schema without compilation")
async def validate_deck(payload: DeckPayload):
    return {
        "status": "valid",
        "title": payload.title,
        "slide_count": len(payload.slides),
        "layouts": [slide.layout for slide in payload.slides],
    }
