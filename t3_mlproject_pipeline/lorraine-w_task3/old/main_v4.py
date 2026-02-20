#!/usr/bin/env python3
from typing import Dict
from pathlib import Path
from datetime import datetime
import os, json, pickle
import numpy as np
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="D602 LAX Delay API")

# --------------------------------------------------------------------------
# Load model & encodings
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # -> code/
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "model" / "finalized_model.pkl"))
ENCODINGS_PATH = Path(os.getenv("ENCODINGS_PATH", BASE_DIR / "model" / "airport_encodings.json"))

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)   # trained Ridge regressor
except Exception as e:
    raise RuntimeError(f"Could not load model at {MODEL_PATH}: {e}")

try:
    with open(ENCODINGS_PATH, "r") as f:
        # Example: {"10140": 0, "10157": 1, ...}
        airport_map: Dict[str, int] = json.load(f)
except Exception as e:
    raise RuntimeError(f"Could not load encodings at {ENCODINGS_PATH}: {e}")

# Model expects this many inputs (post-training)
N_FEATURES = int(getattr(model, "n_features_in_", 0))      # e.g., 89
# Our input is: [one-hot airports] + [dep_seconds, arr_seconds] -> so one-hot length:
EXPECTED_AIRPORT_SLOTS = max(N_FEATURES - 2, 0)            # e.g., 87

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def parse_time_to_seconds(s: str) -> int:
    s = s.replace("T", " ").strip()
    try:
        if " " in s:
            t = datetime.strptime(s, "%Y-%m-%d %H:%M").time()
        else:
            t = datetime.strptime(s, "%H:%M").time()
        return t.hour * 3600 + t.minute * 60 + t.second
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid time '{s}': {e}")

def one_hot_airport(airport_id: str) -> np.ndarray:
    """
    Build a one-hot vector of length EXPECTED_AIRPORT_SLOTS.
    Your JSON may have fewer labels; we still pad to the expected length.
    """
    vec = np.zeros(EXPECTED_AIRPORT_SLOTS, dtype=float)
    idx = airport_map.get(str(airport_id))
    if idx is None:
        raise HTTPException(status_code=400, detail=f"Unknown airport_id '{airport_id}'")
    if 0 <= idx < EXPECTED_AIRPORT_SLOTS:
        vec[idx] = 1.0
    return vec

# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "API is functional"}

@app.get("/predict/delays")
def predict_delays(
    arrival_airport_id: str = Query(..., description="Airport ID from training JSON (e.g., '10140')"),
    departure_time:    str = Query(..., description="Local dep time 'YYYY-mm-dd HH:MM' or 'HH:MM'"),
    arrival_time:      str = Query(..., description="Local arr time 'YYYY-mm-dd HH:MM' or 'HH:MM'")
):
    try:
        oh = one_hot_airport(arrival_airport_id)
        dep_s = parse_time_to_seconds(departure_time)
        arr_s = parse_time_to_seconds(arrival_time)

        # IMPORTANT: no PolynomialFeatures at inference
        X = np.hstack([oh, [dep_s, arr_s]]).reshape(1, -1)

        if X.shape[1] != N_FEATURES:
            raise HTTPException(
                status_code=500,
                detail=f"Feature length {X.shape[1]} != model expects {N_FEATURES} "
                       f"(one-hot slots={EXPECTED_AIRPORT_SLOTS}, dep/arr seconds=2)"
            )

        y = model.predict(X)
        return {"average_delays": float(y[0])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}")

@app.get("/health")
def health():
    return {
        "model_loaded": True,
        "model_path": str(MODEL_PATH),
        "encodings_loaded": True,
        "n_features_in_": N_FEATURES,
        "expected_airport_slots": EXPECTED_AIRPORT_SLOTS,
        "airport_labels_in_json": len(airport_map),
        "alpha": getattr(model, "alpha", None),
    }

# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
