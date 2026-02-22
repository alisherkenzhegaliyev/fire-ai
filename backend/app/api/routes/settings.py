from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.nlp import analyzer

router = APIRouter()

AVAILABLE_MODELS = ["gemma3:1b", "gemma3:4b"]
AVAILABLE_CONCURRENCY = [1, 2, 4, 6, 8]


class NlpSettingsUpdate(BaseModel):
    model_id: str
    concurrency: int


@router.get("/settings")
def get_settings():
    return {
        "model_id": analyzer.MODEL_ID,
        "concurrency": analyzer.CONCURRENCY,
        "available_models": AVAILABLE_MODELS,
        "available_concurrency": AVAILABLE_CONCURRENCY,
    }


@router.post("/settings")
def update_settings(body: NlpSettingsUpdate):
    if body.model_id not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model. Choose from: {AVAILABLE_MODELS}",
        )
    if body.concurrency not in AVAILABLE_CONCURRENCY:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid concurrency. Choose from: {AVAILABLE_CONCURRENCY}",
        )
    analyzer.update_settings(body.model_id, body.concurrency)
    return {"status": "ok", "model_id": body.model_id, "concurrency": body.concurrency}
