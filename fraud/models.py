from typing import List
from pydantic import BaseModel

class FraudRequest(BaseModel):
    merchant_id: str
    country: str

class FraudResponse(BaseModel):
    status: str
    fraud_score: int
    reasons: List[str]

class FraudFeatures(BaseModel):
    velocity_10m: int
    velocity_2m: int
    total_24h: int
    high_value_count: int
    geo_mismatch: int
    round_amount_count: int