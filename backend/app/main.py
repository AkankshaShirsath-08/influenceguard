import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.analysis import analyze
from app.database import save_analysis, get_history  # <--- Ye import add kiya

app = FastAPI(title="InfluenceGuard AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[2]
MOCK_PATH = ROOT / "docs" / "mock_response.json"
METRICS_PATH = Path(__file__).resolve().parents[1] / "ml" / "saved_models" / "metrics.json"


def read_csv(upload: UploadFile, label: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(upload.file)
    except Exception:
        raise HTTPException(status_code=400, detail=f"{label}: valid CSV file nahi hai")
    if df.empty:
        raise HTTPException(status_code=400, detail=f"{label}: file khali hai")
    return df


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/mock")
def mock():
    with open(MOCK_PATH, encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/analyze")
async def analyze_endpoint(
    accounts: UploadFile = File(...),
    comments: UploadFile = File(...),
    growth: UploadFile = File(...),
    influencer_name: str = Form("uploaded_influencer"),
):
    acc = read_csv(accounts, "accounts.csv")
    com = read_csv(comments, "comments.csv")
    gro = read_csv(growth, "growth.csv")
    try:
        result = analyze(acc, com, gro, influencer_name)
        save_analysis(result)  # <--- Database me save karne ke liye ye line add ki
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/metrics")
def metrics():
    with open(METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)


# Naya endpoint history dekhne ke liye
@app.get("/api/history")
def get_analysis_history():
    history = get_history()
    return {"history": history}