import io
from pptx import Presentation
from pptx.util import Inches

from app.core.config import settings
from app.core.exceptions import (
    CompilationError,
    DeckDispatchError,
    UnsupportedLayoutError,
)
from app.engine.layouts.cards import CardsLayoutBuilder
from app.engine.layouts.chart import ChartLayoutBuilder
from app.engine.layouts.image import ImageLayoutBuilder
from app.engine.layouts.process import ProcessLayoutBuilder
from app.engine.layouts.split import SplitLayoutBuilder
from app.engine.layouts.table import TableLayoutBuilder
from app.engine.layouts.title import TitleLayoutBuilder
from app.engine.theme import ResolvedTheme
from app.schemas.deck import DeckPayload


class PresentationCompiler:
    """Headless presentation compiler that translates structured DeckPayload

    into in-memory 16:9 widescreen OpenXML .pptx binaries.
    """

    def compile(self, payload: DeckPayload) -> io.BytesIO:
        """Compile a presentation payload into an in-memory BytesIO buffer.

        Enforces zero disk persistence.
        """
        try:
            prs = Presentation()

            # Enforce OpenXML 16:9 widescreen dimensions
            prs.slide_width = Inches(settings.SLIDE_WIDTH_INCHES)
            prs.slide_height = Inches(settings.SLIDE_HEIGHT_INCHES)

            # Resolve theme colors & font families
            resolved_theme = ResolvedTheme.from_schema(payload.theme)

            # Layout builders registry
            builders = {
                "title": TitleLayoutBuilder(prs, resolved_theme),
                "cards": CardsLayoutBuilder(prs, resolved_theme),
                "table": TableLayoutBuilder(prs, resolved_theme),
                "split": SplitLayoutBuilder(prs, resolved_theme),
                "image": ImageLayoutBuilder(prs, resolved_theme),
                "process": ProcessLayoutBuilder(prs, resolved_theme),
                "flowchart": ProcessLayoutBuilder(prs, resolved_theme),
                "chart": ChartLayoutBuilder(prs, resolved_theme),
            }

            for slide_model in payload.slides:
                layout_key = getattr(slide_model, "layout", None)
                builder = builders.get(layout_key)
                if not builder:
                    raise UnsupportedLayoutError(f"Unsupported slide layout '{layout_key}'.")
                builder.render(slide_model)

            buffer = io.BytesIO()
            prs.save(buffer)
            buffer.seek(0)
            return buffer

        except DeckDispatchError:
            raise
        except Exception as exc:
            raise CompilationError(f"Failed to compile presentation: {exc}") from exc


compiler = PresentationCompiler()
