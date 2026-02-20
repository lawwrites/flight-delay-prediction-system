# tests/test_api.py
import os
from pathlib import Path
import importlib.util
import pytest
from fastapi.testclient import TestClient

# --- set env BEFORE loading the app module so it picks them up on import 
---
REPO_ROOT = Path(__file__).resolve().parents[1]
os.environ["MODEL_PATH"] = str(REPO_ROOT / "code" / "model" / 
"finalized_model.pkl")
os.environ["ENCODINGS_PATH"] = str(REPO_ROOT / "code" / "model" / 
"airport_encodings.json")

# --- load code/app/main.py by absolute path to avoid 'code' stdlib 
conflict ---
MAIN_PATH = REPO_ROOT / "code" / "app" / "main.py"
spec = importlib.util.spec_from_file_location("app_main", MAIN_PATH)
app_main = importlib.util.module_from_spec(spec)
assert spec and spec.loader, "Could not create import spec for main.py"
spec.loader.exec_module(app_main)  # executes the module
app = getattr(app_main, "app")     # FastAPI instance


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
    assert "avg_delays" in body
    assert isinstance(body["avg_delays"], float)

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

