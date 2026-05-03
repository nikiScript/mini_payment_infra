from fastapi import FastAPI
from pydantic import BaseModel
from abc import ABC, abstractmethod

app = FastAPI()

class ChargeRequest(BaseModel):
    amount: float
    currency: str

class ChargeResponse(BaseModel):
    status: str
    provider: str
    provider_id: str
    amount: float
    currency: str
    processed_at: str

class PaymentProvider(ABC):
    name: str

    @abstractmethod
    async def charge(self, req: ChargeRequest) -> ChargeResponse:
        pass