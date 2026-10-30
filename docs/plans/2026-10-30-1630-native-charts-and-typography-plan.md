# Controlled Implementation Plan: Native Office Charts & Typography Budgeting

**Plan ID:** `2026-10-30-1630-native-charts-and-typography-plan`  
**Date:** 2026-10-30  
**Status:** PROPOSED (Awaiting User Checkpoint)  
**Author:** Lead Systems Architect  
**Associated Skill:** `ctl-eng-plan` $\to$ `ctl-eng-checkpoint`

---

## 1. Scope Freeze & Context (Gate 0)

### 1.1 Problem Statement
DeckDispatch currently produces qualitative slides (Cards, Tables, Split, Process Flowcharts, and Showcase Images). However, enterprise presentations require quantitative visual evidence (quarterly ARR, revenue breakdown, customer cohort retention). 

Furthermore, LLMs frequently emit verbose text that overruns bounding boxes because `python-pptx` does not natively auto-shrink text frames to fit shapes.

### 1.2 Core Goals
1. **Native OpenXML Charts:** Add a `chart` layout supporting native PowerPoint Bar Clustered, Column Clustered, Line, and Pie charts using `pptx.chart.data.CategoryChartData`.
2. **Embedded Spreadsheet Editing:** Ensure the generated chart embeds an editable OpenXML worksheet inside the `.pptx` package in memory, allowing PowerPoint users to right-click and "Edit Data".
3. **Typography & Text Budgeting:**
   - Enforce schema-level field budgets (`max_length`) on `CardItem` and slide titles to fail fast on catastrophic LLM verbosity.
   - Implement an adaptive step-down font sizing algorithm in `app/engine/theme.py` that dynamically scales down font points when text exceeds standard length thresholds.
4. **Preserve All Core Invariants:**
   - Zero disk persistence (`io.BytesIO()` memory streams only).
   - 16:9 widescreen dimensions (`13.333"` × `7.5"`).
   - Zero external network calls or binary dependencies during compilation.
   - P95 compilation latency < 200ms.

### 1.3 Strict Non-Goals (Out of Scope for this Plan)
1. **No External Charting / Rasterization Libraries:** Strictly forbidden from importing `matplotlib`, `seaborn`, `plotly`, or headless browser screenshotters. All charts must be native OpenXML vector objects.
2. **No External Cloud Storage Integration:** S3/GCS signed URL generation is deferred to a future cloud adapter unit. Output remains in-memory streaming binary (`io.BytesIO`).
3. **No Stateful Session Storage:** Redis/Valkey multi-turn mutation state is out of scope. The compiler remains strictly stateless.
4. **No Seed Template Disk Persistence:** Pre-baked template `.pptx` file management is deferred to the Template-First roadmap phase.

---

## 2. Architecture & Design Decisions (Gate 1)

### 2.1 Native OpenXML Chart Architecture
`python-pptx` provides direct OpenXML charting primitives:
- `pptx.chart.data.CategoryChartData`
- `pptx.enum.chart.XL_CHART_TYPE` (`COLUMN_CLUSTERED`, `BAR_CLUSTERED`, `LINE`, `PIE`, `AREA`)
- `pptx.enum.chart.XL_LEGEND_POSITION`

When `slide.shapes.add_chart()` is called, `python-pptx` automatically constructs the vector graphic frame (`<c:chart>`) and embeds an Excel workbook part (`xl/worksheets/sheet1.xml`) directly into the `.pptx` zip package in memory.

### 2.2 Deliberate Anti-Pattern Exclusions
- **No Complex Chart Class Hierarchies:** Implement a single, flat `ChartLayoutBuilder` in `app/engine/layouts/chart.py` (aligned with `AGENTS.md` minimalism directives).
- **No Test Hacks in Production Code:** The compiler engine remains strictly protocol-driven.
- **No Magic Coordinate Numbers:** Chart dimensions use the established standard content canvas (`CONTENT_LEFT = 1.0"`, `CONTENT_TOP = 2.15"`, `CONTENT_WIDTH = 11.333"`, `CONTENT_HEIGHT = 4.65"`).

### 2.3 Adaptive Typography Math
```python
def calculate_adaptive_font_size(
    text: str,
    base_pt: int,
    min_pt: int = 10,
    threshold_chars: int = 120,
    step_down_rate: int = 40,
) -> Pt:
    length = len(text.strip())
    if length <= threshold_chars:
        return Pt(base_pt)
    steps = ((length - threshold_chars) // step_down_rate) + 1
    return Pt(max(min_pt, base_pt - steps))
```

---

## 3. Executable Verification Contract (Gate 2)

### 3.1 Verification Commands
```bash
# 1. Full automated unit & integration test suite
uv run pytest -v tests/

# 2. Targeted compiler unit tests
uv run pytest -v tests/test_compiler.py

# 3. Targeted API integration tests
uv run pytest -v tests/test_api.py
```

### 3.2 Invariant & Test Case Matrix

| Test Case | Type | Expected Behavior | Invariant Verified |
| :--- | :--- | :--- | :--- |
| `test_compile_chart_column_clustered` | Unit | Returns binary starting with `PK\x03\x04` | Native vector OpenXML |
| `test_compile_chart_bar_clustered` | Unit | Returns binary starting with `PK\x03\x04` | Native vector OpenXML |
| `test_compile_chart_line` | Unit | Returns binary starting with `PK\x03\x04` | Native vector OpenXML |
| `test_compile_chart_pie` | Unit | Returns binary starting with `PK\x03\x04` | Native vector OpenXML |
| `test_compile_chart_series_colors` | Unit | Custom hex color applied to series fill | Color sanitization |
| `test_adaptive_font_sizing` | Unit | Text > 120 chars steps down from 14pt to 12pt/11pt | Anti-clipping typography |
| `test_api_compile_chart_slide` | API | HTTP 200, valid Content-Disposition and OpenXML headers | End-to-end streaming |
| `test_api_card_budget_validation` | API | HTTP 422 when `CardItem.body` > 300 characters | Fail-fast schema bounds |
| `test_chart_compilation_latency` | Perf | 15-slide deck with charts compiles in < 250ms | Sub-second compute |

---

## 4. Atomic Implementation Units (Gate 3)

### Unit 1: Pydantic v2 Schema Extensions & Text Budgets
- **Target File:** `app/schemas/deck.py`
- **Core Operation:**
  - Add `ChartSeries` (`name`, `values: list[float]`, `color: Optional[str]`).
  - Add `ChartData` (`chart_type: Literal[...]`, `categories`, `series`, `show_legend`, `show_data_labels`).
  - Add `ChartSlide` (`layout: Literal["chart"] = "chart"`, `chart: ChartData`).
  - Register `ChartSlide` in `SlideUnion`.
  - Add `max_length` bounds on `CardItem` (`header: 60`, `body: 300`, `metric: 16`, `tag: 24`).
- **Deliberate Exclusions:** No layout or rendering logic.
- **Verification:** `uv run pytest -v tests/test_compiler.py` (baseline passes).

---

### Unit 2: Adaptive Typography Engine
- **Target File:** `app/engine/theme.py`
- **Core Operation:**
  - Implement `calculate_adaptive_font_size(text, base_pt, min_pt, threshold_chars, step_down_rate) -> Pt`.
  - Wire adaptive font sizing into `CardsLayoutBuilder` and `SplitLayoutBuilder` body paragraphs.
- **Deliberate Exclusions:** No changes to chart engine or external APIs.
- **Verification:** Unit test asserting font points step down dynamically as string length scales.

---

### Unit 3: Native Chart Layout Builder
- **Target File:** `app/engine/layouts/chart.py` [NEW]
- **Core Operation:**
  - Implement `ChartLayoutBuilder(BaseLayoutBuilder)`.
  - Map schema `chart_type` to `pptx.enum.chart.XL_CHART_TYPE`.
  - Populate `CategoryChartData` with categories and series numeric values.
  - Call `slide.shapes.add_chart(chart_type, Inches(1.0), Inches(2.15), Inches(11.333), Inches(4.65), chart_data)`.
  - Style series fills with theme palette (`primary`, `accent`) or series color override.
  - Position legend (`XL_LEGEND_POSITION.TOP`) and configure data labels.
- **Deliberate Exclusions:** No disk writing; entirely in-memory.
- **Verification:** Standalone test generating chart slides and asserting `PK\x03\x04`.

---

### Unit 4: Compiler Dispatcher Integration
- **Target File:** `app/engine/compiler.py`
- **Core Operation:**
  - Import `ChartLayoutBuilder`.
  - Register `"chart": ChartLayoutBuilder(prs, resolved_theme)` in `builders` dictionary.
- **Deliberate Exclusions:** Zero modifications to existing layout builders.
- **Verification:** Multi-layout deck compilation test including `ChartSlide`.

---

### Unit 5: Verification Suite & Documentation
- **Target Files:** `tests/test_compiler.py`, `tests/test_api.py`, `docs/SCHEMA_GUIDE.md`, `README.md`
- **Core Operation:**
  - Add comprehensive unit tests for all 4 chart types (column, bar, line, pie).
  - Add API integration test for chart compilation and schema validation boundaries.
  - Add performance latency assertion (< 250ms for decks containing charts).
  - Document the `chart` layout in `docs/SCHEMA_GUIDE.md` with copy-pasteable JSON examples.
- **Verification:** `uv run pytest -v tests/` (all tests passing green).

---

## 5. Enterprise Roadmap Architecture (Subsequent Phases)

To ensure this plan completely captures the full scope from `production_grade_evolution_plan.md`, here is the architectural roadmap for the remaining recommendations:

### Phase 2: Seed PPTX Templates (Recommendation 1)
- **Concept:** Separate brand design (master slide layouts, corporate backgrounds, logos) from Python code by supporting seed presentation files.
- **Implementation Strategy:**
  - Introduce an optional `template_id: Optional[str]` field on `DeckPayload`.
  - Store validated enterprise master `.pptx` templates in an in-memory registry or bundled directory (`app/templates/`).
  - Instead of `Presentation()`, initialize via `Presentation(template_stream)` where `template_stream` is an in-memory `io.BytesIO` buffer of the seed template.
  - Map Pydantic slide fields to named slide master placeholders (`slide.placeholders`).

### Phase 3: Cloud Storage & Multi-Turn Mutation (Recommendations 4 & 5)
- **Direct Cloud Integration (Recommendation 4):**
  - Add query parameter support: `POST /v1/decks/compile?output=binary` (default) vs `POST /v1/decks/compile?output=url`.
  - When `output=url` is requested, an async cloud storage client streams the `io.BytesIO` presentation buffer directly to an S3 or GCS bucket, sets a TTL (e.g. 2 hours), and returns `{ "download_url": "https://storage.googleapis.com/.../deck.pptx?Expires=..." }`.
  - Preserves the zero-disk-persistence invariant while giving agent runtimes durable links.
- **Multi-Turn Mutation API (Recommendation 5):**
  - Implement a stateless or Redis-backed session endpoint:
    - `POST /v1/decks/session`: Creates a session, returns `session_id`.
    - `PATCH /v1/decks/session/{session_id}/slides/{slide_index}`: Accepts a single slide patch (e.g., updating bullet points or mutating a card metric) without resending the entire 15-slide JSON payload.
    - `GET /v1/decks/session/{session_id}/export`: Compiles and streams the final `.pptx`.
  - Reduces LLM token consumption by ~80% during iterative chat turns.

---

## 6. Checkpoint & Affirmation

Does this execution roadmap look good to begin **Unit 1** via `/ctl-eng-checkpoint`?

