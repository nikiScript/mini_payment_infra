import hashlib
import os

import httpx
from fastapi import HTTPException, Header, Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from db.migrations.schemas.merchants import ApiKey

class PaymentRequest(BaseModel):
    amount: int
    currency: str
    country: str

router = APIRouter()

@router.post("/payments")
async def payments(
        req: PaymentRequest,
        x_api_key: str = Header(...),
        db: AsyncSession = Depends(get_db),
):

    hashed = hashlib.sha256(x_api_key.encode()).hexdigest()
    # query api_key table
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == hashed)
    )
    api_key_record = result.scalar_one_or_none()

    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    print("authorized")
    print("[GATEWAY]: sending to fraud")
    fraud = await send_to_fraud(
        merchant_id=api_key_record.merchant_id,
        payment_request=req
    )
    if fraud["status"] == "blocked":
        return fraud
    print("passed")
    print("[GATEWAY]: sending to router")
    router_response = await send_to_router(
        merchant_id=api_key_record.merchant_id,
        payment_request=req
    )
    return router_response
    # send to router


async def send_to_router(
        merchant_id: str,
        payment_request: PaymentRequest,
):
    ROUTER_URL = os.getenv("ROUTER_URL", "http://routing:8001/router")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{ROUTER_URL}",
                json=payment_request.model_dump(),
                headers={"Content-Type": "application/json",
                         "merchant-id": str(merchant_id)
                         },
                timeout=5,
            )
        except Exception as e:
            return {"error": str(e)}

        return resp.json()

async def send_to_fraud(
        merchant_id: str,
        payment_request: PaymentRequest,
):
    FRAUD_URL = os.getenv("FRAUD_URL", "http://fraud:8004/fraud")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{FRAUD_URL}",
                json={
                    **payment_request.model_dump(),
                    "merchant_id": str(merchant_id)
                },
                timeout=5,
            )
        except Exception as e:
            return {"error": str(e)}

        return resp.json()

