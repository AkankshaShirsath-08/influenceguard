import json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="InfluenceGuard AI")

# CORS: frontend ko backend se baat karne dene ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_PATH = Path(__file__).resolve().parents[2] / "docs" / "mock_response.json"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    # Abhi mock data return ho raha hai, baad me real ML se replace karenge
    with open(MOCK_PATH, encoding="utf-8") as f:
        return json.load(f)