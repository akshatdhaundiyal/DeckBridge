# DeckBridge Architecture & System Design

DeckBridge is a high-performance headless presentation compiler that translates declarative JSON slide payloads directly into valid, widescreen (16:9) Microsoft OpenXML `.pptx` presentations using **FastAPI** and **python-pptx**.

---

## 1. Architectural Philosophy & Invariants

DeckBridge was designed to solve the failure modes of client-side presentation rendering (e.g., `PptxGenJS`, headless browser screen-scraping, and canvas rasterization) in agentic runtimes.

```
┌──────────────────────────────────────┐
│  Client / LLM Orchestrator           │
│  - Semantic Structuring              │
│  - Narrative Design                  │
└──────────────────┬───────────────────┘
                   │ POST /v1/decks/compile (JSON)
                   ▼
┌──────────────────────────────────────┐
│  DeckBridge Microservice             │
│  ├── Pydantic v2 Schema Gate         │
│  ├── Dynamic Coordinate Engine       │
│  ├── In-Memory Image Scaler (Pillow) │
│  └── python-pptx OpenXML Assembler   │
└──────────────────┬───────────────────┘
                   │ io.BytesIO Stream (< 250ms)
                   ▼
┌──────────────────────────────────────┐
│  Native Vector OpenXML .pptx         │
│  - 100% Editable Shapes & Text       │
│  - Zero Font Metric Clipping         │
└──────────────────────────────────────┘
```

### The Non-Negotiable Invariants

1. **Strict Decoupling**: All OpenXML compilation happens server-side via `python-pptx`. No browser canvas rendering or client-side DOM dependencies are permitted.
2. **Zero Disk Persistence**: Generated presentations and intermediate images are processed exclusively in RAM (`io.BytesIO`). No files are written to `/tmp` or persistent storage during compilation.
3. **OpenXML Widescreen Compliance**:
   - Slide dimensions must be widescreen 16:9: `13.333` inches wide by `7.5` inches high (`prs.slide_width = Inches(13.333)`, `prs.slide_height = Inches(7.5)`).
   - Hex colors are strictly sanitized to `RGBColor(r, g, b)`.
   - Text frames must enforce zero-margins (`margin_top = margin_bottom = margin_left = margin_right = 0`) to eliminate font metric clipping.
   - Word wrap must be set to `True` on all multi-line text bodies.
4. **Dynamic Coordinate Engine**: No hardcoded coordinate numbers inside layout loops. All column and row placements are computed via deterministic mathematical bounding functions.
5. **Sub-Second Performance**: Pure in-memory compute with zero external network calls or thread locks during `POST /v1/decks/compile`. P95 compilation latency is < 250ms for decks up to 15 slides.

---

## 2. Dynamic Coordinate Engine

Hardcoding coordinates causes brittle layouts when the number of elements varies. DeckBridge uses a dynamic bounding formula in [`app/engine/coordinates.py`](file:///d:/lab/projects/DeckBridge/app/engine/coordinates.py):

### Column Spacing Formula
```python
def get_column_bounds(
    total_cols: int,
    left: float = 1.0,
    total_width: float = 11.333,
    gap: float = 0.35,
) -> tuple[list[float], float]:
    col_w = (total_width - (gap * (total_cols - 1))) / total_cols
    left_positions = [left + i * (col_w + gap) for i in range(total_cols)]
    return left_positions, col_w
```

- **Symmetric Margins**: With widescreen width of `13.333"`, a content canvas of `total_width = 11.333"` starting at `left = 1.0"` yields perfectly balanced `1.0"` margins on both left and right edges (`1.0 + 11.333 = 12.333`, leaving `1.0"` to `13.333`).
- **Row Spacing**: Similarly, `get_row_bounds()` divides the `4.65"` content vertical space between `top = 2.15"` and `6.8"`, guaranteeing no bottom clipping.

---

## 3. In-Memory Image Engine & Aspect Ratio Containment

DeckBridge ingests images as base64 data strings without making external network calls.

### Contain & Center Algorithm
To prevent images from being stretched or distorted when placed in presentation boxes, [`app/engine/images.py`](file:///d:/lab/projects/DeckBridge/app/engine/images.py) inspects the natural dimensions with Pillow and calculates proportional containment bounds:

$$\text{aspect}_{\text{img}} = \frac{W_{\text{orig}}}{H_{\text{orig}}}, \quad \text{aspect}_{\text{box}} = \frac{W_{\text{box}}}{H_{\text{box}}}$$

- If $\text{aspect}_{\text{img}} > \text{aspect}_{\text{box}}$:
  $$W_{\text{fit}} = W_{\text{box}}, \quad H_{\text{fit}} = \frac{W_{\text{box}}}{\text{aspect}_{\text{img}}}$$
- If $\text{aspect}_{\text{img}} \le \text{aspect}_{\text{box}}$:
  $$H_{\text{fit}} = H_{\text{box}}, \quad W_{\text{fit}} = H_{\text{box}} \times \text{aspect}_{\text{img}}$$

The image is then centered horizontally and vertically inside the container box:
$$\text{left}_{\text{fit}} = \text{left}_{\text{box}} + \frac{W_{\text{box}} - W_{\text{fit}}}{2}, \quad \text{top}_{\text{fit}} = \text{top}_{\text{box}} + \frac{H_{\text{box}} - H_{\text{fit}}}{2}$$

All validation, format verification (PNG, JPEG, WebP), and scaling operations are executed in memory with a strict 10MB payload ceiling.

---

## 4. Modular Layout Architecture

Each slide layout is implemented as an isolated builder inheriting from `BaseLayoutBuilder` in [`app/engine/layouts/`](file:///d:/lab/projects/DeckBridge/app/engine/layouts/):

```
app/engine/layouts/
├── base.py       # Slide creation, header canvas (kicker, title, subtitle), zero-margins
├── title.py      # Hero title layout with accent line
├── cards.py      # 1 to 4 container cards, metric callouts, and image thumbnails
├── table.py      # Native OpenXML tables with zebra rows and header styling
├── split.py      # 2-column comparative layout with bullets and images
├── image.py      # Showcase image frame with aspect ratio containment and captions
└── process.py    # Vector flowchart pipelines (horizontal and vertical with connecting arrows)
```

The main presentation compiler loop [`app/engine/compiler.py`](file:///d:/lab/projects/DeckBridge/app/engine/compiler.py) initializes the presentation, dispatches each slide model to its respective builder, and streams the resulting `.pptx` directly from an `io.BytesIO()` buffer.

