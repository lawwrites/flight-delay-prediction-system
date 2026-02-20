from typing import Union
import pandas as pd
import numpy as np
from fastapi import FastAPI
import json


app = FastAPI()

lax_delays = '/Users/lawhea1214/Documents/WGU/602/lorraine-w_task3/code/model/finalized_model.pkl'

@app.get("/api-endpoint")
def lax_delays():
    pass


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
