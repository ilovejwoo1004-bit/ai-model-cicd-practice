from fastapi import FastAPI
import pickle
import numpy as np

app = FastAPI()

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

@app.get("/")
def home():
    return {"message": "AI Model API is running"}

@app.get("/predict")
def predict(value: float):
    X = np.array([[value]])
    pred = model.predict(X)[0]
    return {
        "input": value,
        "prediction": int(pred)
    }

