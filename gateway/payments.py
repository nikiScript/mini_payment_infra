import hashlib

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


    return {"status": "authorized", "merchant_id": api_key_record.merchant_id, "PaymentRequest": req}
