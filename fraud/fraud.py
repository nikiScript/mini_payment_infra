from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from rules import enforce_rules
from scoring import fraud_score
from query_transaction import get_transactions_data
from models import FraudRequest, FraudFeatures, FraudResponse

app = FastAPI()

@app.post("/fraud")
async def fraud(
        req: FraudRequest,
        db: AsyncSession = Depends(get_db)
):
    resp = await get_transactions_data(req.merchant_id, req.country, db)
    features = FraudFeatures(**resp)
    review = enforce_rules(features)
    total_score = fraud_score(features)

    if review["status"] == "blocked":
        return FraudResponse(
            status=review["status"],
            fraud_score=total_score,
            reasons=[review["reason"]]
        )

    if total_score > 80:
        return FraudResponse(
            status="blocked",
            fraud_score=total_score,
            reasons=["high fraud score"]
        )
    if total_score > 50:
        return FraudResponse(
            status="review",
            fraud_score=total_score,
            reasons=["high fraud score"]
        )
    else:
        return FraudResponse(
            status="allowed",
            fraud_score=total_score,
            reasons=["low risk"]
        )