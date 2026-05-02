from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from rules import enforce_rules
from scoring import fraud_score
from query_transaction import get_transactions_data

class FraudFeatures(BaseModel):
    velocity_10m: int
    total_24h: int
    high_value_count: int
    geo_mismatch: int
    round_amount_count: int

class Request(BaseModel):
    merchant_id: str
    country: str

app = FastAPI()

@app.post("/fraud")
async def fraud(
        req: Request,
        db: AsyncSession
):
    resp = await get_transactions_data(req.merchant_id, req.country, db)
    features = FraudFeatures(**resp)
    review = enforce_rules(features)

    if review.status == "blocked":
        return review

    total_score = fraud_score(features)

    if total_score > 150:
        return {
            "status": "blocked",
            "reason": "high fraud score",
        }
    if 60 < total_score < 150:
        return {
            "status": "review",
            "reason": "suspicious activity",
        }
    else:
        return {
            "status": "authorized",
            "reason": "low risk"
        }