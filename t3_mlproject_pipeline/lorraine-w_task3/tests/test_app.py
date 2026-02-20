# tests/test_api.py
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient


# --- set env BEFORE importing the app so it picks them up on import ---
REPO_ROOT = Path(__file__).resolve().parents[1]
os.environ["MODEL_PATH"] = str(REPO_ROOT / "src" / "model" / "finalized_model.pkl")
os.environ["ENCODINGS_PATH"] = str(REPO_ROOT / "src" / "model" / "airport_encodings.json")

# now it's safe to import the FastAPI app
from src.app.main import app



@pytest.fixture(scope="module")
def client():
    """Setup: create a TestClient; Teardown: auto close on context exit."""
    with TestClient(app) as c:
        yield c


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "API is functional"}


def test_predict_valid(client):
    params = {
        "arrival_airport_id": "10140",  # must exist in your JSON
        "departure_time": "15:25",
        "arrival_time": "17:30",
    }
    r = client.get("/predict/delays", params=params)
    assert r.status_code == 200
    body = r.json()
    assert "average_delays" in body
    assert isinstance(body["average_delays"], float)


def test_predict_invalid_airport(client):
    params = {
        "arrival_airport_id": "BADCODE",
        "departure_time": "15:25",
        "arrival_time": "17:30",
    }
    r = client.get("/predict/delays", params=params)
    assert r.status_code == 400
    data = r.json()
    assert ("error" in data) or ("detail" in data)


def test_predict_invalid_time(client):
    params = {
        "arrival_airport_id": "10140",
        "departure_time": "notatime",
        "arrival_time": "17:30",
    }
    r = client.get("/predict/delays", params=params)
    assert r.status_code == 400
