from fastapi.testclient import TestClient

from backend.app.ingestion.seed import seed_demo_data
from backend.app.main import app
from backend.app.processing.risk import compute_all_risk_scores


def test_latest_risk_endpoint_returns_seeded_rows():
    seed_demo_data(days=80)
    compute_all_risk_scores()
    client = TestClient(app)
    response = client.get("/api/risk/latest")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20
    assert {"stock_id", "total_score", "risk_level"}.issubset(data[0].keys())


def test_unknown_stock_returns_404():
    client = TestClient(app)
    response = client.get("/api/stocks/9999/summary")
    assert response.status_code == 404
