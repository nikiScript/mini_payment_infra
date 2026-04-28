import hashlib
import secrets

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database import get_db
from db.migrations.schemas.merchants import Merchants, ApiKey

router = APIRouter()

class RegisterName(BaseModel):
    name: str


@router.post("/register")
async def register(
        req: RegisterName,
        db: AsyncSession = Depends(get_db),
):
    # create new name
    merchants = Merchants(name=req.name)
    db.add(merchants)
    await db.flush()

    # generate api key
    raw_key = secrets.token_hex(32)
    hashed = hashlib.sha256(raw_key.encode()).hexdigest()

    api_key = ApiKey(merchant_id=merchants.id, key_hash=hashed)
    db.add(api_key)
    await db.commit()

    return {"merchant_id": merchants.id, "api_key": raw_key}

