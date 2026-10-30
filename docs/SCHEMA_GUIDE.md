# DeckDispatch Slide Schema Guide

DeckDispatch slide types are discriminated on the `layout` attribute. All schemas support both `camelCase` (standard frontend/JSON style) and `snake_case` (Python style).

---

## 1. Top-Level Deck Payload

```json
{
  "title": "Presentation Title",
  "theme": { ... },
  "slides": [ ... ]
}
```

### Theme Configuration (`theme`)
All colors must be valid 6-character hex strings (with or without `#`) or 3-character shorthand.

| Field | Default | Description |
| :--- | :--- | :--- |
| `primaryColor` | `"0F172A"` | Main brand color for headers, table header fills, and titles |
| `accentColor` | `"2563EB"` | Accent color for kickers, metric callouts, and flowchart arrows |
| `cardBg` | `"F8FAFC"` | Background fill color for cards, zebra rows, and process nodes |
| `cardBorder` | `"E2E8F0"` | Stroke border color for cards and shapes |
| `textColor` | `"0F172A"` | Body text color |
| `mutedColor` | `"64748B"` | Subtitle and kicker text color |
| `backgroundColor` | `"FFFFFF"` | Global slide background color |
| `fontFamily` | `"Calibri"` | Global font family |

### Slide-Level Theme Overrides
Any slide can set `backgroundOverride` to:
- `"dark"`: Sets dark navy background (`#0F172A`) with high-contrast light text (`#F8FAFC`).
- `"light"`: Sets clean white background (`#FFFFFF`) with dark text (`#0F172A`).
- Any custom hex code (e.g., `"#1E293B"`). Text colors auto-adjust based on background luminance.

---

## 2. Slide Layouts

### 2.1 Title Slide (`layout: "title"`)
Hero centerpiece presentation title slide with brand accent bar.

```json
{
  "layout": "title",
  "kicker": "SERIES A",
  "title": "Redefining Enterprise Automation",
  "subtitle": "Q4 2026 Strategy & Growth Metrics",
  "backgroundOverride": "dark"
}
```

---

### 2.2 Cards Slide (`layout: "cards"`)
Dynamic grid of 1 to 4 executive cards. Supports prominent metric callouts (`metric`), category pills (`tag`), and optional thumbnail images (`imageBase64`).

```json
{
  "layout": "cards",
  "kicker": "MARKET HEADWINDS",
  "title": "Three Catalysts Driving Our Expansion",
  "subtitle": "Shift toward autonomous agentic presentation compilers",
  "cards": [
    {
      "header": "Fragmented Runtimes",
      "body": "Enterprises struggle with brittle client-side DOM rendering scripts.",
      "metric": "$4.2B",
      "tag": "MARKET"
    },
    {
      "header": "High Maintenance",
      "body": "Engineering teams waste 30% of their sprints fixing browser parsers.",
      "metric": "30%",
      "tag": "EFFICIENCY"
    },
    {
      "header": "Scalable Infrastructure",
      "body": "Headless serverless engines replace client-side bundle bloat.",
      "metric": "10x",
      "tag": "GROWTH"
    }
  ]
}
```

---

### 2.3 Table Slide (`layout: "table"`)
Native OpenXML table with themed header fill, alternating zebra row striping, and zero-margin cell padding.

```json
{
  "layout": "table",
  "kicker": "COMPETITIVE MATRIX",
  "title": "Head-to-Head Architecture Breakdown",
  "table": {
    "headers": ["Capability", "Legacy Web Tools", "DeckDispatch"],
    "columnWidths": [3.5, 4.0, 3.833],
    "rows": [
      ["Vector Shapes", "No (Rasterized / Canvas)", "Yes (Native OpenXML)"],
      ["Sandbox Resilient", "No (Iframe blocks)", "Yes (In-Memory Stream)"],
      ["P95 Latency", "> 3,500ms", "< 200ms"],
      ["Font Clipping", "Frequent (Browser metrics)", "Zero (Explicit zero-margins)"]
    ]
  }
}
```

---

### 2.4 Split Slide (`layout: "split"`)
Two-column comparative layout for Before/After, Problem/Solution, or Feature comparisons. Supports headers, body narrative, bullet points, and optional embedded images.

```json
{
  "layout": "split",
  "kicker": "ARCHITECTURE COMPARISON",
  "title": "Client-Side DOM vs Headless OpenXML",
  "leftColumn": {
    "header": "Client-Side Runtimes",
    "body": "Compiling OpenXML inside the browser DOM causes frequent failure modes:",
    "items": [
      "Iframe download sandboxes block binary blob exports",
      "Heavy client-side bundles (PptxGenJS + canvas)",
      "Unpredictable font metric clipping and text wrapping"
    ]
  },
  "rightColumn": {
    "header": "DeckDispatch Engine",
    "body": "Pure headless server-side presentation compilation via python-pptx:",
    "items": [
      "In-memory io.BytesIO streaming with zero disk I/O",
      "Strict OpenXML 16:9 compliance (13.333\" x 7.5\")",
      "Sub-250ms deterministic compilation for decks up to 15 slides"
    ]
  }
}
```

---

### 2.5 Image Slide (`layout: "image"`)
Showcase slide for architecture diagrams, UI screenshots, or photography. The engine automatically inspects image dimensions and applies **Contain & Center** math, guaranteeing no image stretching or distortion.

```json
{
  "layout": "image",
  "kicker": "SYSTEM DIAGRAM",
  "title": "End-to-End Presentation Compilation Flow",
  "subtitle": "Declarative JSON to In-Memory OpenXML Binary",
  "imageBase64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
  "caption": "Figure 1: High-level compiler data flow diagram."
}
```

---

### 2.6 Process & Flowchart Slide (`layout: "process"` or `"flowchart"`)
Generates 2 to 5 sequential process steps using native PowerPoint vector AutoShapes (`rounded_rectangle`, `diamond`, `oval`, `rectangle`) and automatic connecting vector arrows (`RIGHT_ARROW` or `DOWN_ARROW`).

#### Horizontal Flow (`direction: "horizontal"`, default):
```json
{
  "layout": "process",
  "direction": "horizontal",
  "kicker": "COMPILATION PIPELINE",
  "title": "Four Stages of OpenXML Presentation Assembly",
  "steps": [
    {
      "stepNumber": 1,
      "title": "Schema Gate",
      "body": "Pydantic v2 validates discriminated union slide payloads.",
      "shapeType": "rounded_rectangle"
    },
    {
      "stepNumber": 2,
      "title": "Coordinate Math",
      "body": "Dynamic bounding formulas compute column and row margins.",
      "shapeType": "diamond"
    },
    {
      "stepNumber": 3,
      "title": "Vector Assembly",
      "body": "python-pptx builds native OpenXML slides and text frames.",
      "shapeType": "rounded_rectangle"
    },
    {
      "stepNumber": 4,
      "title": "Memory Stream",
      "body": "Streams io.BytesIO buffer directly to client.",
      "shapeType": "oval"
    }
  ]
}
```

#### Vertical Stack (`direction: "vertical"`):
```json
{
  "layout": "process",
  "direction": "vertical",
  "kicker": "SECURITY CHECKS",
  "title": "In-Memory Image Validation Loop",
  "steps": [
    {
      "title": "Header Strip",
      "body": "Extracts raw base64 string from data URI prefix."
    },
    {
      "title": "Size Ceiling",
      "body": "Enforces 10MB maximum payload restriction."
    },
    {
      "title": "Pillow Verification",
      "body": "Validates image format and dimensions in RAM."
    }
  ]
}
```

---

### 2.7 Chart Slide (`layout: "chart"`)
Embeds native Microsoft OpenXML charts (Column Clustered, Bar Clustered, Line, Pie, Area) with an embedded editable Excel worksheet. Users opening the `.pptx` in PowerPoint or Google Slides can right-click the chart and choose **Edit Data** to update numbers directly.

#### Column / Bar Clustered Chart:
```json
{
  "layout": "chart",
  "kicker": "FINANCIAL PERFORMANCE",
  "title": "Quarterly ARR Trajectory",
  "subtitle": "Year-over-Year Comparative Growth",
  "chart": {
    "chartType": "column_clustered",
    "categories": ["Q1", "Q2", "Q3", "Q4"],
    "series": [
      {
        "name": "2025",
        "values": [1.2, 1.8, 2.4, 3.1]
      },
      {
        "name": "2026",
        "values": [2.0, 3.2, 4.5, 6.0],
        "color": "2563EB"
      }
    ],
    "showLegend": true,
    "showDataLabels": true
  }
}
```

#### Pie Chart (Market Share / Distribution):
```json
{
  "layout": "chart",
  "kicker": "MARKET SHARE",
  "title": "Enterprise Cloud Footprint",
  "chart": {
    "chartType": "pie",
    "categories": ["North America", "EMEA", "APAC", "LATAM"],
    "series": [
      {
        "name": "Market Share %",
        "values": [42.5, 28.0, 21.5, 8.0]
      }
    ],
    "showLegend": true,
    "showDataLabels": true
  }
}
```

