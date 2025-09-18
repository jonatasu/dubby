from fastapi.testclient import TestClient
from app.main import app


def test_index_page():
    """Test that the main page loads correctly."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_status_page():
    """Test that the status page loads correctly."""
    client = TestClient(app)
    response = client.get("/status")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_api_status():
    """Test that the API status endpoint works."""
    client = TestClient(app)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "python" in data
    assert "ffmpeg" in data