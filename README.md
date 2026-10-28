# DeckDispatch

> High-performance, headless presentation compiler that transforms structured JSON into native 16:9 widescreen Microsoft OpenXML (`.pptx`) presentations in sub-second latency.

[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![python-pptx](https://img.shields.io/badge/python--pptx-1.0.2-orange.svg)](https://python-pptx.readthedocs.io/)
[![Tests](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)]()

---

## Why DeckDispatch?

Large Language Models excel at semantic structuring and narrative design, but fail when asked to compile binary OpenXML files directly in client-side browser sandboxes (dropping CDN dependencies, hitting iframe download security blocks, or producing corrupted XML).

**DeckDispatch** decouples content generation from file compilation:
- **Zero Client-Side Sandbox Failures**: Replaces `PptxGenJS`, canvas rendering, and browser screenshot hacks with pure server-side OpenXML compilation via `python-pptx`.
- **Zero Disk Persistence**: Presentation files are assembled purely in memory and streamed directly via `io.BytesIO()`.
- **OpenXML 16:9 Compliance**: Enforces exact widescreen dimensions (`13.333"` × `7.5"`), hex color sanitization, explicit zero-margin text frames, and forced word-wrapping to prevent font metric clipping.
- **Sub-Second Latency**: P95 compilation time < 250ms for presentations up to 15 slides.
- **Native Vector Shapes & Flowcharts**: Generates real editable vector shapes, arrows, and table structures—never rasterized images.

---

## Supported Slide Layouts

DeckDispatch supports discriminated union slide types with dual `camelCase` and `snake_case` schema compatibility:

1. **`TitleSlide` (`layout: "title"`)**: Hero presentation title with eyebrow kicker, high-impact headline, subtitle, and brand accent line.
2. **`CardsSlide` (`layout: "cards"`)**: Dynamic grid of 1 to 4 executive cards supporting large metric callouts (`"$4.2B"`, `"10x"`), category pills, and optional thumbnail images.
3. **`TableSlide` (`layout: "table"`)**: Native OpenXML tables with styled header rows, alternating zebra striping, and custom column widths.
4. **`SplitSlide` (`layout: "split"`)**: 2-column comparative layout for Before/After, Problem/Solution, or Feature comparisons.
5. **`ImageSlide` (`layout: "image"`)**: Showcase image frame with in-memory aspect ratio containment (no distortion or stretching) and captions.
6. **`ProcessSlide` (`layout: "process"` or `"flowchart"`)**: 2 to 5 sequential process steps using native PowerPoint vector shapes (`rounded_rectangle`, `diamond`, `oval`, `rectangle`) with connecting vector arrows in both horizontal and vertical orientations.

---

## Quickstart

### 1. Installation
```bash
# Using uv (recommended)
uv venv
.venv\Scripts\Activate.ps1  # or source .venv/bin/activate on Linux/macOS
uv pip install -r requirements.txt
```

### 2. Run the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) to access the interactive Swagger UI.

### 3. Compile a Slide Deck
```bash
curl -X POST "http://localhost:8000/v1/decks/compile" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Series A Pitch",
       "slides": [
         {
           "layout": "title",
           "kicker": "SERIES A",
           "title": "Autonomous Presentation Runtimes",
           "subtitle": "Q4 Strategy"
         }
       ]
     }' \
     --output presentation.pptx
```

### 4. Run Automated Tests
```bash
pytest -v tests/
```

---

## Documentation Index

Explore the comprehensive documentation under [`docs/`](file:///d:/lab/projects/DeckBridge/docs/):

- **[Architecture & Invariants](file:///d:/lab/projects/DeckBridge/docs/ARCHITECTURE.md)**: System design, non-negotiable invariants, coordinate math formulas, and OpenXML compliance guarantees.
- **[API Reference](file:///d:/lab/projects/DeckBridge/docs/API_REFERENCE.md)**: Complete endpoint documentation, request/response headers, error codes, and curl/Python/TypeScript invocation snippets.
- **[Slide Schema Guide](file:///d:/lab/projects/DeckBridge/docs/SCHEMA_GUIDE.md)**: Detailed schema breakdown with copy-pasteable JSON examples for every layout type and theme overrides.
- **[Getting Started & Deployment](file:///d:/lab/projects/DeckBridge/docs/GETTING_STARTED.md)**: Setup, local development, Docker deployment, and testing guide.
- **[Developer Rules & Agent Instructions](file:///d:/lab/projects/DeckBridge/AGENTS.md)**: Invariant enforcement, minimalism directives, and code quality guidelines.

---

## License
MIT
