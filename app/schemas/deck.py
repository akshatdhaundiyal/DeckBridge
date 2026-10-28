from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model allowing both camelCase and snake_case field access."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


class CardItem(CamelModel):
    header: Optional[str] = Field(None, description="Card headline or title")
    title: Optional[str] = Field(None, description="Alternative alias for headline")
    body: str = Field(..., description="Card narrative or description")
    metric: Optional[str] = Field(None, description="Prominent metric callout (e.g. '$4.2B', '10x')")
    tag: Optional[str] = Field(None, description="Category pill or tag")
    image_base64: Optional[str] = Field(None, description="Optional base64 image thumbnail inside card")
    accent_color: Optional[str] = Field(None, description="Optional hex color override")

    @property
    def display_header(self) -> str:
        return self.header or self.title or ""


class TableData(CamelModel):
    headers: list[str] = Field(..., min_length=1, description="Table column names")
    rows: list[list[str]] = Field(..., description="Table row cell values")
    column_widths: Optional[list[float]] = Field(None, description="Optional column widths in inches")


class ColumnContent(CamelModel):
    header: Optional[str] = Field(None, description="Column header/title")
    body: Optional[str] = Field(None, description="Column descriptive text")
    items: Optional[list[str]] = Field(None, description="Bullet points or key takeaways")
    image_base64: Optional[str] = Field(None, description="Optional base64 image in column")
    accent_color: Optional[str] = Field(None, description="Hex color override")


class ProcessStep(CamelModel):
    step_number: Optional[int] = Field(None, description="Step number (defaults to sequential 1..N)")
    title: str = Field(..., min_length=1, description="Step title or action name")
    body: Optional[str] = Field(None, description="Brief description of the process step")
    shape_type: Literal["rounded_rectangle", "rectangle", "diamond", "oval"] = "rounded_rectangle"
    accent_color: Optional[str] = Field(None, description="Optional step color override")


# --- Slide Models with Discriminated Union ---


class BaseSlide(CamelModel):
    kicker: Optional[str] = Field(None, description="Category / eyebrow kicker")
    title: str = Field(..., min_length=1, description="Main slide title")
    subtitle: Optional[str] = Field(None, description="Supporting subtitle")
    background_override: Optional[str] = Field(
        None, description="Slide background override: 'dark', 'light', or custom hex (#0F172A)"
    )


class TitleSlide(BaseSlide):
    layout: Literal["title"] = "title"


class CardsSlide(BaseSlide):
    layout: Literal["cards"] = "cards"
    cards: list[CardItem] = Field(..., min_length=1, max_length=4, description="1 to 4 cards")


class TableSlide(BaseSlide):
    layout: Literal["table"] = "table"
    table: TableData


class SplitSlide(BaseSlide):
    layout: Literal["split"] = "split"
    left_column: ColumnContent
    right_column: ColumnContent


class ImageSlide(BaseSlide):
    layout: Literal["image"] = "image"
    image_base64: str = Field(..., description="Base64 encoded image string or data URI")
    caption: Optional[str] = Field(None, description="Optional image caption")


class ProcessSlide(BaseSlide):
    layout: Literal["process", "flowchart"] = "process"
    direction: Literal["horizontal", "vertical"] = "horizontal"
    steps: list[ProcessStep] = Field(..., min_length=2, max_length=5, description="2 to 5 steps")


SlideUnion = Annotated[
    Union[TitleSlide, CardsSlide, TableSlide, SplitSlide, ImageSlide, ProcessSlide],
    Field(discriminator="layout"),
]


class DeckTheme(CamelModel):
    primary_color: str = Field("0F172A", description="Primary brand / heading color (hex)")
    accent_color: str = Field("2563EB", description="Secondary accent / highlight color (hex)")
    card_bg: str = Field("F8FAFC", description="Card background fill color (hex)")
    text_color: str = Field("0F172A", description="Default body text color (hex)")
    muted_color: str = Field("64748B", description="Muted text & kicker color (hex)")
    background_color: str = Field("FFFFFF", description="Slide background fill color (hex)")
    card_border: str = Field("E2E8F0", description="Card border stroke color (hex)")
    font_family: str = Field("Calibri", description="Global font family")


class DeckPayload(CamelModel):
    title: str = Field("DeckDispatch Presentation", description="Presentation title")
    theme: DeckTheme = Field(default_factory=DeckTheme)
    slides: list[SlideUnion] = Field(..., min_length=1, description="List of structured slides")
