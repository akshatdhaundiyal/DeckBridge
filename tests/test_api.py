import time
import pytest
import httpx

from app.main import app

pytestmark = pytest.mark.anyio

ZIP_MAGIC_SIGNATURE = b"PK\x03\x04"

PRD_PAYLOAD = {
    "title": "Series A Pitch Deck",
    "theme": {
        "primaryColor": "0F172A",
        "accentColor": "2563EB",
        "cardBg": "F8FAFC",
        "textColor": "0F172A",
        "mutedColor": "64748B",
        "fontFamily": "Calibri",
    },
    "slides": [
        {
            "layout": "title",
            "kicker": "SERIES A",
            "title": "Redefining Enterprise Workflows",
            "subtitle": "Q4 2026 Strategy & Growth Metrics",
        },
        {
            "layout": "cards",
            "kicker": "MARKET OPPORTUNITY",
            "title": "Three Macro Headwinds We Capitalize On",
            "subtitle": "Shift toward autonomous agentic runtimes",
            "cards": [
                {
                    "header": "Fragmented Runtimes",
                    "body": "Enterprises struggle with brittle LLM client scripts.",
                    "metric": "$4.2B",
                },
                {
                    "header": "High Maintenance",
                    "body": "Developers spend 30% of engineering time fixing brittle parsers.",
                    "metric": "30%",
                },
                {
                    "header": "Scalable Infrastructure",
                    "body": "Decoupled headless engines replace client-side bloat.",
                    "metric": "10x",
                },
            ],
        },
        {
            "layout": "table",
            "kicker": "COMPETITIVE MATRIX",
            "title": "Feature Breakdown by Category",
            "table": {
                "headers": ["Feature", "Legacy Web Tools", "DeckBridge"],
                "rows": [
                    ["Vector Shapes", "No (Rasterized)", "Yes (Native OpenXML)"],
                    ["Sandbox Resilient", "No (Iframe blocks)", "Yes (Serverless Stream)"],
                    ["Latency", "> 3000ms", "< 200ms"],
                ],
            },
        },
    ],
}


@pytest.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["service"] == "DeckBridge"


async def test_compile_prd_contract(async_client):
    response = await async_client.post("/v1/decks/compile", json=PRD_PAYLOAD)
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="Series_A_Pitch_Deck.pptx"'
    )
    assert response.content.startswith(ZIP_MAGIC_SIGNATURE)
    assert len(response.content) > 1000


async def test_validate_endpoint(async_client):
    response = await async_client.post("/v1/decks/validate", json=PRD_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "valid"
    assert data["title"] == "Series A Pitch Deck"
    assert data["slide_count"] == 3
    assert data["layouts"] == ["title", "cards", "table"]


async def test_validation_error_max_cards_exceeded(async_client):
    invalid_payload = {
        "title": "Too Many Cards",
        "slides": [
            {
                "layout": "cards",
                "title": "5 Cards Test",
                "cards": [{"header": f"Card {i}", "body": "Body"} for i in range(5)],
            }
        ],
    }
    response = await async_client.post("/v1/decks/compile", json=invalid_payload)
    assert response.status_code == 422


async def test_validation_error_invalid_layout(async_client):
    invalid_payload = {
        "title": "Invalid Layout",
        "slides": [{"layout": "non_existent_layout", "title": "Test Slide"}],
    }
    response = await async_client.post("/v1/decks/compile", json=invalid_payload)
    assert response.status_code == 422


async def test_validation_error_corrupted_image(async_client):
    payload = {
        "title": "Corrupt Image",
        "slides": [
            {
                "layout": "image",
                "title": "Corrupt",
                "imageBase64": "not_valid_base64_data!!!",
            }
        ],
    }
    response = await async_client.post("/v1/decks/compile", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "IMAGE_PROCESSING_ERROR"


async def test_compile_chart_slide_endpoint(async_client):
    payload = {
        "title": "Quarterly Financials",
        "slides": [
            {
                "layout": "chart",
                "kicker": "FINANCIAL PERFORMANCE",
                "title": "Quarterly ARR Trajectory",
                "chart": {
                    "chartType": "column_clustered",
                    "categories": ["Q1", "Q2", "Q3", "Q4"],
                    "series": [
                        {"name": "2025", "values": [1.2, 1.8, 2.4, 3.1]},
                        {"name": "2026", "values": [2.0, 3.2, 4.5, 6.0]},
                    ],
                    "showLegend": True,
                    "showDataLabels": True,
                },
            }
        ],
    }
    response = await async_client.post("/v1/decks/compile", json=payload)
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert response.content.startswith(ZIP_MAGIC_SIGNATURE)


async def test_validation_error_card_body_budget_exceeded(async_client):
    payload = {
        "title": "Overflow Test",
        "slides": [
            {
                "layout": "cards",
                "title": "Exceed Budget",
                "cards": [
                    {
                        "header": "Normal",
                        "body": "X" * 301,  # max_length is 300
                    }
                ],
            }
        ],
    }
    response = await async_client.post("/v1/decks/compile", json=payload)
    assert response.status_code == 422


async def test_validation_error_invalid_color(async_client):
    payload = {
        "title": "Invalid Color",
        "theme": {"primaryColor": "ZZZZZZ"},
        "slides": [{"layout": "title", "title": "Test Slide"}],
    }
    response = await async_client.post("/v1/decks/compile", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_COLOR_ERROR"


async def test_compilation_latency_15_slides(async_client):
    """Verify 15-slide presentation compilation satisfies the sub-second latency requirement."""
    slides = []
    for i in range(15):
        if i % 3 == 0:
            slides.append(
                {
                    "layout": "title",
                    "title": f"Slide {i + 1}: Strategic Milestone",
                    "kicker": "SECTION",
                }
            )
        elif i % 3 == 1:
            slides.append(
                {
                    "layout": "cards",
                    "title": f"Slide {i + 1}: Growth Highlights",
                    "cards": [
                        {"header": "Metric 1", "body": "Key takeaway", "metric": "$10M"},
                        {"header": "Metric 2", "body": "Key takeaway", "metric": "95%"},
                    ],
                }
            )
        else:
            slides.append(
                {
                    "layout": "table",
                    "title": f"Slide {i + 1}: Data Breakdown",
                    "table": {
                        "headers": ["Metric", "Q1", "Q2"],
                        "rows": [["Revenue", "100", "150"], ["Margin", "20%", "25%"]],
                    },
                }
            )

    payload = {"title": "Performance Benchmark Deck", "slides": slides}

    # Warm-up request
    await async_client.post("/v1/decks/compile", json=payload)

    # Measured run
    start_time = time.perf_counter()
    response = await async_client.post("/v1/decks/compile", json=payload)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    assert response.status_code == 200
    assert response.content.startswith(ZIP_MAGIC_SIGNATURE)
    # Target latency: Sub-second (< 1000ms)
    assert elapsed_ms < 1000, f"Compilation took {elapsed_ms:.1f}ms, exceeding sub-second requirement."
