#!/usr/bin/env python3
from typing import Dict
from pathlib import Path
from datetime import datetime
import os, json, pickle
import numpy as np

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="D602 LAX Delay API")
# ------------------------------------------------------------------------------
#loads models and encodings
# ------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent  # -> code/
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "model" / "finalized_model.pkl"))
ENCODINGS_PATH = Path(os.getenv("ENCODINGS_PATH", BASE_DIR / "model" / "airport_encodings.json"))

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)   # Your trained Ridge regressor
except Exception as e:
    raise RuntimeError(f"Could not load model at {MODEL_PATH}: {e}")

try:
    with open(ENCODINGS_PATH, "r") as f:
        # JSON created in Task 2: {"10140": 0, "10157": 1, ...}
        airport_map: Dict[str, int] = json.load(f)
except Exception as e:
    raise RuntimeError(f"Could not load encodings at {ENCODINGS_PATH}: {e}")


# infer expected feature count from the model
N_FEATURES = int(getattr(model, "n_features_in_", 0))  # e.g., 89
EXPECTED_AIRPORT_SLOTS = max(N_FEATURES - 2, 0)        # one-hot airports + 2 time features

# ------------------------------------------------------------------------------
# Helper functions 
# ------------------------------------------------------------------------------

def parse_time_to_seconds(s: str) -> int:
    """
    Accepts 'YYYY-mm-dd HH:MM' or 'HH:MM' and returns seconds since midnight.
    """
    s = s.replace("T", " ").strip()
    try:
        if " " in s:
            t = datetime.strptime(s, "%Y-%m-%d %H:%M").time()
        else:
            t = datetime.strptime(s, "%H:%M").time()
        return t.hour*3600 + t.minute*60 + t.second
    except Exception as e:
        # mirror lab’s 400 handling via HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid time '{s}': {e}")

def one_hot_airport(airport_id: str) -> np.ndarray:
    """
    Build the one-hot vector for DEST_AIRPORT using the Task 2 label map.
    Keys are DOT airport IDs as strings (e.g., '10140'), not IATA ('LAX').
    """
    vec = np.zeros(EXPECTED_AIRPORT_SLOTS, dtype=float)
    idx = airport_map.get(str(airport_id))
    if idx is None:
        # Lab abort(400) equivalent: reject unknown airports (you can relax to zeros if you prefer)
        raise HTTPException(status_code=400, detail=f"Unknown airport_id '{airport_id}'")
    if 0 <= idx < EXPECTED_AIRPORT_SLOTS:
        vec[idx] = 1.0
    return vec

# ------------------------------------------------------------------------------
# Resources / Routes
# ------------------------------------------------------------------------------

@app.get("/")
def root():
    # Lab’s “API is functional”
    return {"message": "API is functional"}

@app.get("/predict/delays")
def predict_delays(
    arrival_airport_id: str = Query(..., description="Airport ID from training JSON (e.g., '10140')"),
    departure_time:    str = Query(..., description="Local dep time 'YYYY-mm-dd HH:MM' or 'HH:MM'"),
    arrival_time:      str = Query(..., description="Local arr time 'YYYY-mm-dd HH:MM' or 'HH:MM'")
):
    """
    Returns: {"average_departure_delay": <float minutes>}
    Matches the rubric’s required endpoint and parameters. :contentReference[oaicite:1]{index=1}
    """
    # Build feature row exactly like Task 2: one-hot airport + time seconds
    oh = one_hot_airport(arrival_airport_id)
    dep_s = parse_time_to_seconds(departure_time)
    arr_s = parse_time_to_seconds(arrival_time)
    X = np.hstack([oh, [dep_s, arr_s]]).reshape(1, -1)

    if X.shape[1] != N_FEATURES:
        # Lab-style explicit error
        raise HTTPException(
            status_code=500,
            detail=f"Feature length {X.shape[1]} != model expects {N_FEATURES} "
                   f"(one-hot slots={EXPECTED_AIRPORT_SLOTS}, dep/arr seconds=2)"
        )

    try:
        y = model.predict(X)
        return {"average_departure_delay": float(y[0])}
    except Exception as e:
        # Lab’s bad_request + abort(400) equivalent
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}")

@app.get("/health")
def health():
    # Handy like lab’s diagnostics; not required but useful
    return {
        "model_loaded": True,\
        "model_path": str(MODEL_PATH),\
        "encodings_loaded": True,\
        "n_features_in_": N_FEATURES,\
        "expected_airport_slots": EXPECTED_AIRPORT_SLOTS,\
        "airport_labels_in_json": len(airport_map),\
        "alpha": getattr(model, "alpha", None),\
    }

# ------------------------------------------------------------------------------
# Error handling 
# ------------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # mirror Flask’s make_response(jsonify({'error': '...'}), code)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

