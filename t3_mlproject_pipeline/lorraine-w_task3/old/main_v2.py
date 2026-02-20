from typing import Union
import pandas as pd
import numpy as np
from fastapi import FastAPI
import pickle
import json
import os

app = FastAPI(title="D602 LAX Delay API")


#---Load articats (relative paths that work locally & in Docker) ---
BASE_DIR = Path(__file__).resolve().parent.parent #points to code/
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR/"model"/"finalized_model.pkl"))
ENCODINGS_PATH = BASE_DIR / "model"/"aireport_encodings.json"


with open(MODEL_PATH, "rb") as pkl:
    model = pickle.load(pkl)

airport_encodings = {}
if ENCODINGS_PATH.exists():
    with open(ENCODINGS_PATH, "r") as encodings:
        airport_encodings = json.load(encodings)


# ---- ENDPOINTS ----

@app.get("/api-endpoint")
def home():
    return {"message": "API is functional"}

@app.get("/predict/")
def predict(DEPARTURE_TIME: int, DEPARTURE_DELAY: int, ARRIVAL_TIME: int, ARRIVAL_DELAY: int):

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
