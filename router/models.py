import enum
from typing import Optional, List
from pydantic import BaseModel

class PaymentRequest(BaseModel):
    amount: int
    currency: str
    country: str

class Provider(enum.Enum):
    stripe = "stripe"
    paypal = "paypal"
    adyen = "adyen"

class RouterResponse(BaseModel):
    provider: Optional[Provider]
    reason: str
    attempted_providers: List[str]
