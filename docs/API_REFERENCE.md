# DeckDispatch API Reference

DeckDispatch provides a lightweight, stateless REST API for validating and compiling declarative JSON slide payloads into native `.pptx` presentation files.

---

## Base URL
```
http://localhost:8000
```

---

## Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status and version check |
| `POST` | `/v1/decks/compile` | Compile slide payload into binary `.pptx` stream |
| `POST` | `/v1/decks/validate` | Validate payload schema without compiling |

---

## 1. Health Check

### `GET /health`
Verifies that the DeckDispatch service is healthy and responsive.

#### Request
```bash
curl -X GET http://localhost:8000/health
```

#### Response (200 OK)
```json
{
  "status": "healthy",
  "service": "DeckDispatch",
  "version": "1.0.0"
}
```

---

## 2. Compile Presentation

### `POST /v1/decks/compile`
Compiles a structured presentation payload into a 16:9 widescreen Microsoft OpenXML `.pptx` binary stream.

#### Headers
- **Request `Content-Type`**: `application/json`
- **Response `Content-Type`**: `application/vnd.openxmlformats-officedocument.presentationml.presentation`
- **Response `Content-Disposition`**: `attachment; filename="<sanitized_deck_title>.pptx"`

#### Request Body
Accepts both `camelCase` and `snake_case` keys:

```json
{
  "title": "Series A Pitch Deck",
  "theme": {
    "primaryColor": "0F172A",
    "accentColor": "2563EB",
    "cardBg": "F8FAFC",
    "textColor": "0F172A",
    "mutedColor": "64748B",
    "fontFamily": "Calibri"
  },
  "slides": [
    {
      "layout": "title",
      "kicker": "SERIES A",
      "title": "Redefining Enterprise Workflows",
      "subtitle": "Q4 2026 Strategy & Growth Metrics"
    },
    {
      "layout": "cards",
      "kicker": "MARKET OPPORTUNITY",
      "title": "Three Macro Headwinds We Capitalize On",
      "cards": [
        {
          "header": "Fragmented Runtimes",
          "body": "Enterprises struggle with brittle LLM client scripts.",
          "metric": "$4.2B"
        },
        {
          "header": "High Maintenance",
          "body": "Developers spend 30% of engineering time fixing brittle parsers.",
          "metric": "30%"
        },
        {
          "header": "Scalable Infrastructure",
          "body": "Decoupled headless engines replace client-side bloat.",
          "metric": "10x"
        }
      ]
    }
  ]
}
```

#### Response (200 OK)
Binary file stream (`PK\x03\x04` OpenXML zip signature).

#### Error Responses (422 Unprocessable Entity)
When validation fails or domain rules are violated:

```json
{
  "error": "IMAGE_PROCESSING_ERROR",
  "detail": "Failed to decode base64 image payload: ..."
}
```

Common error codes:
- `COMPILATION_ERROR`: python-pptx compilation failure.
- `INVALID_COLOR_ERROR`: Malformed hex color string.
- `IMAGE_PROCESSING_ERROR`: Corrupted base64 payload or file size > 10MB.
- `UNSUPPORTED_LAYOUT_ERROR`: Unrecognized slide layout type.

---

## 3. Validate Presentation Schema

### `POST /v1/decks/validate`
Validates the JSON payload against the Pydantic v2 schema without triggering `.pptx` compilation.

#### Request Body
Same schema as `POST /v1/decks/compile`.

#### Response (200 OK)
```json
{
  "status": "valid",
  "title": "Series A Pitch Deck",
  "slide_count": 2,
  "layouts": ["title", "cards"]
}
```

---

## 4. Code Examples

### cURL
```bash
curl -X POST "http://localhost:8000/v1/decks/compile" \
     -H "Content-Type: application/json" \
     -d @deck_payload.json \
     --output presentation.pptx
```

### Python (httpx)
```python
import httpx

payload = {
    "title": "Quarterly Review",
    "slides": [
        {"layout": "title", "title": "Q3 Executive Review"}
    ]
}

response = httpx.post("http://localhost:8000/v1/decks/compile", json=payload)
response.raise_for_status()

with open("quarterly_review.pptx", "wb") as f:
    f.write(response.content)

print(f"Presentation saved successfully ({len(response.content)} bytes).")
```

### TypeScript / Node.js (fetch)
```typescript
import * as fs from 'fs';

async function compileDeck() {
  const payload = {
    title: "Product Launch",
    slides: [
      { layout: "title", title: "Next-Gen AI Platform" }
    ]
  };

  const response = await fetch("http://localhost:8000/v1/decks/compile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Compilation failed: ${JSON.stringify(error)}`);
  }

  const arrayBuffer = await response.arrayBuffer();
  fs.writeFileSync("Product_Launch.pptx", Buffer.from(arrayBuffer));
  console.log("Presentation downloaded successfully.");
}

compileDeck();
```
